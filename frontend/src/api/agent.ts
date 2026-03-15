const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SearchCriteria {
    location: string;
    property_type: string;
    bedrooms?: number;
    bathrooms?: number;
    max_price?: number;
    rent_frequency: 'monthly' | 'yearly';
    additional_requirements?: string;
}

export interface SSEEvent {
    type: 'progress' | 'interrupt' | 'report' | 'error';
    agent?: string;
    progress?: number;
    thread_id?: string;
    properties?: any[];
    data?: any;
    message?: string;
}

/** Open SSE stream to /api/stream. Calls onEvent for each parsed event. */
export function streamSearch(
    criteria: SearchCriteria,
    onEvent: (e: SSEEvent) => void,
    onDone: () => void
) {
    const timestamp = Date.now().toString();
    const body = JSON.stringify({
        messages: [{ role: 'user', content: buildPrompt(criteria) }],
        timestamp,
    });

    const ctrl = new AbortController();

    fetch(`${API}/api/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        signal: ctrl.signal,
    }).then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let buf = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buf += decoder.decode(value, { stream: true });
            const lines = buf.split('\n');
            buf = lines.pop()!;
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const evt: SSEEvent = JSON.parse(line.slice(6));
                        if (evt.type === 'interrupt' || evt.type === 'report') {
                            evt.thread_id = `thread-${timestamp}`;
                        }
                        onEvent(evt);
                    } catch { /* skip malformed */ }
                }
            }
        }
        onDone();
    }).catch((err) => {
        if (err.name !== 'AbortError') {
            onEvent({ type: 'error', message: err.message });
        }
    });

    return ctrl; // caller can ctrl.abort()
}

/** Open SSE stream to /api/stream-resume after user approves properties. */
export function streamResume(
    threadId: string,
    approvedIds: string[],
    onEvent: (e: SSEEvent) => void,
    onDone: () => void
) {
    const body = JSON.stringify({
        thread_id: threadId,
        approved_properties: approvedIds,
    });

    const ctrl = new AbortController();

    fetch(`${API}/api/stream-resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        signal: ctrl.signal,
    }).then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let buf = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buf += decoder.decode(value, { stream: true });
            const lines = buf.split('\n');
            buf = lines.pop()!;
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        onEvent(JSON.parse(line.slice(6)));
                    } catch { /* skip malformed */ }
                }
            }
        }
        onDone();
    }).catch((err) => {
        if (err.name !== 'AbortError') {
            onEvent({ type: 'error', message: err.message });
        }
    });

    return ctrl;
}

function buildPrompt(c: SearchCriteria): string {
    const parts = [`Find ${c.property_type} properties in ${c.location}`];
    if (c.bedrooms) parts.push(`${c.bedrooms} bedrooms`);
    if (c.bathrooms) parts.push(`${c.bathrooms} bathrooms`);
    if (c.max_price) parts.push(`budget ${c.max_price} ${c.rent_frequency}`);
    if (c.additional_requirements) parts.push(c.additional_requirements);
    return parts.join(', ');
}

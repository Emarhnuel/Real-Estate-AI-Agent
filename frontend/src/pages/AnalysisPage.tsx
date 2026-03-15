import { useState, useRef } from 'react';
import { Header } from '../components/Header';
import { AgentForm } from '../components/AgentForm';
import { PropertySelector } from '../components/PropertySelector';
import { streamSearch, streamResume } from '../api/agent';
import type { SearchCriteria, SSEEvent } from '../api/agent';
import { Brain, ScanSearch, CheckCircle2, AlertCircle, MapPin, BedDouble, Bath, Home, Star, ThumbsUp, ThumbsDown, ArrowRight } from 'lucide-react';

type PageState = 'IDLE' | 'STREAMING' | 'WAITING_USER_INPUT' | 'RESUMING' | 'COMPLETED' | 'ERROR';

const AGENT_LABELS: Record<string, string> = {
    property_search: 'Searching Properties',
    location_analysis: 'Analyzing Locations',
    interior_decorator: 'Generating Designs',
};

export function AnalysisPage() {
    const [pageState, setPageState] = useState<PageState>('IDLE');
    const [progress, setProgress] = useState(0);
    const [activeAgent, setActiveAgent] = useState('');
    const [interruptProps, setInterruptProps] = useState<any[]>([]);
    const [threadId, setThreadId] = useState('');
    const [finalResults, setFinalResults] = useState<any>(null);
    const [decoratedImages, setDecoratedImages] = useState<Record<string, string>>({});
    const [errorMessage, setErrorMessage] = useState('');
    const abortRef = useRef<AbortController | null>(null);

    const loadDecoratedImage = async (propertyId: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/interior-image/${propertyId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.decorated_image_base64) {
                    setDecoratedImages(prev => ({ ...prev, [propertyId]: data.decorated_image_base64 }));
                }
            }
        } catch (error) {
            console.error("Failed to load decorated image for", propertyId, error);
        }
    };

    const handleEvent = (e: SSEEvent) => {
        if (e.type === 'progress') {
            setProgress(e.progress ?? 0);
            if (e.agent) setActiveAgent(AGENT_LABELS[e.agent] || e.agent);
        } else if (e.type === 'interrupt') {
            setInterruptProps(e.properties ?? []);
            if (e.thread_id) setThreadId(e.thread_id);
            setPageState('WAITING_USER_INPUT');
        } else if (e.type === 'report') {
            setFinalResults(e.data);
            setPageState('COMPLETED');
            
            // Load decorated images for all properties in the report
            if (e.data?.properties) {
                e.data.properties.forEach((prop: any) => {
                    const propId = prop.id || prop.property_id;
                    if (propId) loadDecoratedImage(propId);
                });
            }
        } else if (e.type === 'error') {
            setErrorMessage(e.message || 'Unknown error');
            setPageState('ERROR');
        }
    };

    const handleStart = (criteria: SearchCriteria) => {
        setPageState('STREAMING');
        setProgress(0);
        setActiveAgent('Initializing...');
        setErrorMessage('');

        abortRef.current = streamSearch(criteria, handleEvent, () => {
            /* SSE stream ended — if not in a terminal state, it's an error */
            setPageState((prev) => (prev === 'STREAMING' ? 'ERROR' : prev));
        });
    };

    const handleApproval = (selected: { id: string; style: string }[]) => {
        setPageState('RESUMING');
        setProgress(50);
        setActiveAgent('Analyzing Locations');

        abortRef.current = streamResume(
            threadId,
            selected.map((s) => s.id),
            handleEvent,
            () => {
                setPageState((prev) => (prev === 'RESUMING' ? 'ERROR' : prev));
            }
        );
    };

    const handleRetry = () => {
        setPageState('IDLE');
        setProgress(0);
    };

    const reset = () => {
        abortRef.current?.abort();
        setPageState('IDLE');
        setProgress(0);
        setFinalResults(null);
        setDecoratedImages({});
        setInterruptProps([]);
        setErrorMessage('');
    };

    return (
        <div className="min-h-screen bg-slate-50 selection:bg-brand-100 selection:text-brand-900">
            <Header />
            <main className="container mx-auto px-6 pt-32 pb-20">

                {/* IDLE */}
                {pageState === 'IDLE' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <AgentForm onSubmit={handleStart} isLoading={false} />
                    </div>
                )}

                {/* STREAMING / RESUMING */}
                {(pageState === 'STREAMING' || pageState === 'RESUMING') && (
                    <div className="max-w-xl mx-auto text-center animate-in fade-in duration-500">
                        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-8 shadow-xl relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-20" />
                            {pageState === 'STREAMING' ? (
                                <ScanSearch className="w-10 h-10 text-brand-600 animate-pulse" />
                            ) : (
                                <Brain className="w-10 h-10 text-gold-500 animate-pulse" />
                            )}
                        </div>

                        <h2 className="text-2xl font-bold text-slate-900 mb-2">{activeAgent}</h2>
                        <p className="text-slate-500 mb-8">
                            {pageState === 'STREAMING'
                                ? 'Our AI agents are scanning listing sites...'
                                : 'Running location analysis and generating designs...'}
                        </p>

                        {/* Progress bar */}
                        <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                            <div
                                className="h-full bg-brand-600 rounded-full transition-all duration-500"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <p className="text-sm text-slate-400 mt-2">{progress}% complete</p>
                    </div>
                )}

                {/* WAITING_USER_INPUT */}
                {pageState === 'WAITING_USER_INPUT' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <PropertySelector
                            properties={interruptProps}
                            onApprove={handleApproval}
                            onRetry={handleRetry}
                        />
                    </div>
                )}

                {/* COMPLETED */}
                {pageState === 'COMPLETED' && finalResults && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="text-center mb-12">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 text-green-700 font-bold mb-4">
                                <CheckCircle2 className="w-5 h-5" />
                                Analysis Complete
                            </div>
                            <h2 className="text-3xl font-bold text-slate-900 font-serif">Your Intelligence Report</h2>
                            <p className="text-slate-500 mt-4 max-w-2xl mx-auto text-lg leading-relaxed">{finalResults.summary}</p>
                        </div>
                        
                        <div className="space-y-12">
                            {finalResults.properties?.map((prop: any, idx: number) => (
                                <div key={idx} className="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100 flex flex-col md:flex-row">
                                    {/* Left Column: Details & Location */}
                                    <div className="flex-[3] p-8 md:p-10 border-b md:border-b-0 md:border-r border-slate-100">
                                        <div className="mb-6">
                                            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-brand-50 text-brand-700 rounded-full text-sm font-semibold mb-3">
                                                <Home className="w-4 h-4" />
                                                {prop.property_type || 'Property'}
                                            </div>
                                            <h3 className="text-2xl font-bold text-slate-900 mb-2 font-serif leading-tight">{prop.address}</h3>
                                            <div className="text-3xl font-bold text-brand-600 mb-4">{prop.price}</div>
                                            
                                            <div className="flex items-center gap-6 text-slate-600 mb-6">
                                                <div className="flex items-center gap-2"><BedDouble className="w-5 h-5 text-slate-400" /> {prop.bedrooms} Beds</div>
                                                <div className="flex items-center gap-2"><Bath className="w-5 h-5 text-slate-400" /> {prop.bathrooms} Baths</div>
                                            </div>
                                            <p className="text-slate-600 leading-relaxed text-sm mb-6 line-clamp-4">{prop.description}</p>
                                            
                                            {prop.listing_url && prop.listing_url !== '#' && (
                                                <a href={prop.listing_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-brand-600 font-bold hover:text-brand-700 hover:underline">
                                                    View Original Listing <ArrowRight className="w-4 h-4" />
                                                </a>
                                            )}
                                        </div>

                                        {/* Location Analysis */}
                                        <div className="bg-slate-50 rounded-2xl p-6">
                                            <h4 className="font-bold text-slate-900 mb-4 flex items-center gap-2"><MapPin className="w-5 h-5 text-brand-600" /> Location Intelligence</h4>
                                            
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                {prop.location_analysis?.pros?.length > 0 && (
                                                    <div>
                                                        <div className="text-sm font-semibold text-green-700 mb-3 flex items-center gap-1.5"><ThumbsUp className="w-4 h-4" /> Highlights</div>
                                                        <ul className="space-y-2">
                                                            {prop.location_analysis.pros.map((pro: string, i: number) => (
                                                                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                                                                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-1.5 shrink-0" />
                                                                    <span>{pro}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                                
                                                {prop.location_analysis?.cons?.length > 0 && (
                                                    <div>
                                                        <div className="text-sm font-semibold text-red-700 mb-3 flex items-center gap-1.5"><ThumbsDown className="w-4 h-4" /> Drawbacks</div>
                                                        <ul className="space-y-2">
                                                            {prop.location_analysis.cons.map((con: string, i: number) => (
                                                                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                                                                    <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 shrink-0" />
                                                                    <span>{con}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Nearby Amenities Detail */}
                                            {prop.location_analysis?.nearby_pois && (
                                                <div className="mt-6 pt-5 border-t border-slate-200">
                                                    <h5 className="text-sm font-semibold text-slate-700 mb-3">Nearby Amenities</h5>
                                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                                        {Object.entries(prop.location_analysis.nearby_pois).map(([category, pois]: [string, any]) => {
                                                            const poiList = Array.isArray(pois) ? pois : [];
                                                            if (poiList.length === 0) return null;
                                                            const label = category.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
                                                            return (
                                                                <div key={category} className="bg-white rounded-xl p-3 border border-slate-100">
                                                                    <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
                                                                    <ul className="space-y-1.5">
                                                                        {poiList.map((poi: any, i: number) => (
                                                                            <li key={i} className="text-sm text-slate-700 flex items-center justify-between gap-2">
                                                                                <span className="truncate">{poi.name}</span>
                                                                                <span className="text-xs text-slate-400 font-medium whitespace-nowrap">
                                                                                    {poi.distance_meters >= 1000 
                                                                                        ? `${(poi.distance_meters / 1000).toFixed(1)}km` 
                                                                                        : `${Math.round(poi.distance_meters)}m`}
                                                                                </span>
                                                                            </li>
                                                                        ))}
                                                                    </ul>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    
                                    {/* Right Column: Interior Design */}
                                    <div className="flex-[2] p-8 md:p-10 bg-slate-900 text-white flex flex-col justify-center">
                                        <div className="mb-6">
                                            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white/10 text-white rounded-full text-sm font-semibold mb-3">
                                                <Star className="w-4 h-4 text-gold-400" />
                                                Interior Redesign
                                            </div>
                                            <h4 className="text-xl font-bold mb-2">AI Rendered Vision</h4>
                                            <p className="text-slate-400 text-sm">Style Profile: <span className="text-white font-medium">{prop.interior_decoration?.style || 'Selected Style'}</span></p>
                                        </div>
                                        
                                        <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-black aspect-square md:aspect-[4/5] flex-shrink-0 group">
                                            {decoratedImages[prop.id] ? (
                                                <img 
                                                    src={decoratedImages[prop.id].startsWith('data:image') 
                                                        ? decoratedImages[prop.id] 
                                                        : `data:image/jpeg;base64,${decoratedImages[prop.id]}`} 
                                                    alt="AI Decorated Interior" 
                                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                                />
                                            ) : (
                                                <div className="absolute inset-0 flex items-center justify-center text-white/50 bg-slate-800 text-center p-6">
                                                    No rendered image available for this property.
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-12 text-center border-t border-slate-200 pt-12">
                            <button onClick={reset} className="bg-slate-900 text-white px-8 py-4 rounded-xl font-bold hover:scale-105 transition-all shadow-lg hover:shadow-xl">
                                Start Another Search
                            </button>
                        </div>
                    </div>
                )}

                {/* ERROR */}
                {pageState === 'ERROR' && (
                    <div className="max-w-md mx-auto text-center animate-in fade-in duration-500">
                        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
                        <h2 className="text-xl font-bold text-slate-900 mb-2">Something went wrong</h2>
                        <p className="text-slate-500 mb-8">{errorMessage}</p>
                        <button onClick={reset} className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold hover:scale-105 transition-transform">
                            Try Again
                        </button>
                    </div>
                )}

            </main>
        </div>
    );
}

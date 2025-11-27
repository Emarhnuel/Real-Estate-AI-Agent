---
inclusion: always
---

# Project Context: AI Real Estate Co-Pilot

## Project Structure

```
ai-real-estate-copilot/
├── src/                       # Python backend
│   ├── agent.py               # All agents + SupervisorState
│   ├── main.py                # FastAPI server entry point
│   ├── prompts.py             # System prompts for all agents
│   ├── tools.py               # Tavily, Google Places tools
│   ├── models.py              # Pydantic models
│   └── utils.py               # Helper functions
├── frontend/                  # Next.js frontend
│   └── src/
│       ├── pages/             # Next.js pages
│       │   ├── index.tsx      # Home page
│       │   ├── agent.tsx      # Agent interaction (protected)
│       │   ├── _app.tsx       # App wrapper with ClerkProvider
│       │   ├── sign-in/       # Clerk sign-in
│       │   ├── sign-up/       # Clerk sign-up
│       │   └── profile/       # User profile (protected)
│       ├── components/        # React components
│       │   ├── ChatInterface.tsx
│       │   ├── Navigation.tsx
│       │   ├── PropertyReportView.tsx
│       │   ├── PropertyReviewPanel.tsx
│       │   ├── PropertySearchForm.tsx
│       │   └── ui/            # Reusable UI components
│       ├── lib/               # Utility functions
│       ├── styles/            # Global styles
│       └── middleware.ts      # Clerk route protection
├── tests/                     # Integration tests
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── pyproject.toml             # Python project config (uv)
```

## Technology Stack

**Backend:**
- Deep Agents (LangGraph) for agent orchestration
- FastAPI in `src/main.py`
- fastapi-clerk-auth for authentication
- MemorySaver for development state persistence
- uv for Python package management

**Frontend:**
- Next.js (Pages Router) in `frontend/` directory
- Clerk for authentication
- Tailwind CSS for styling

## API Endpoints

All endpoints in: `src/main.py`

```
POST /api/invoke   - Start agent conversation
POST /api/resume   - Resume after interrupt
GET  /api/state    - Get agent state
```

Protected by Clerk using `fastapi-clerk-auth`

## Authentication Flow

1. User signs in with Clerk on frontend
2. Frontend gets JWT token with `getToken()`
3. Frontend sends JWT in Authorization header to `/api`
4. FastAPI validates JWT with `ClerkHTTPBearer`
5. API extracts user_id from `creds.decoded["sub"]`
6. Thread ID format: `{user_id}-{timestamp}`

## Agent Architecture

- **Supervisor Agent** - Coordinates conversation and sub-agents
- **Property Search Sub-Agent** - Finds listings with Tavily
- **Location Analysis Sub-Agent** - Analyzes locations with Google Places

## State Management

- Agent state stored via MemorySaver checkpointer (development)
- Filesystem for context offloading (/properties/, /locations/)
- Thread ID format: `{user_id}-{timestamp}`

## Key Files

- `src/main.py` - FastAPI server entry point
- `src/agent.py` - Agent definitions and graph
- `frontend/src/pages/agent.tsx` - Main agent interaction page
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project config

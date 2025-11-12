---
inclusion: always
---

# Project Context: AI Real Estate Co-Pilot

## Project Structure

```
ai-real-estate-copilot/
├── api/
│   └── index.py       # Single FastAPI file with all endpoints
├── src/
│   ├── agent.py       # All agents + SupervisorState
│   ├── prompts.py     # System prompts for all agents
│   ├── tools.py       # Tavily, Mapbox tools
│   ├── models.py      # Pydantic models
│   └── utils.py       # Helper functions
├── pages/
│   ├── index.tsx      # Home page
│   ├── agent.tsx      # Agent interaction (protected)
│   ├── sign-in/       # Clerk sign-in
│   ├── sign-up/       # Clerk sign-up
│   └── profile/       # User profile (protected)
├── components/        # React components
├── tests/             # Integration tests
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── pyproject.toml     # Python project config (uv)
```

## Technology Stack

**Backend:**
- Deep Agents (LangGraph) for agent orchestration
- FastAPI in single `api/index.py` file (deployed as Vercel serverless function)
- fastapi-clerk-auth for authentication
- Vercel Postgres for state persistence
- uv for Python package management

**Frontend:**
- Next.js (Pages Router)
- Clerk for authentication
- Tailwind CSS for styling
- Deployed to Vercel

## API Endpoints

All endpoints in single file: `api/index.py`

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
- **Location Analysis Sub-Agent** - Analyzes locations with Mapbox

## State Management

- Agent state stored in Vercel Postgres via checkpointer
- Filesystem for context offloading (/properties/, /locations/)
- Thread ID format: `{user_id}-{timestamp}`

## Deployment

Everything deploys to Vercel:
- Frontend pages (Next.js)
- Single API endpoint at `/api` (FastAPI serverless function)
- Vercel Postgres database
- Clerk authentication

**Key files for deployment:**
- `api/index.py` - FastAPI app
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel configuration

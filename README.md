# AI Real Estate Co-Pilot

An intelligent, conversational AI agent that automates property search and analysis using Deep Agents (LangGraph).



## Features

- Natural language property search
- Automated property listing discovery with Tavily
- Location analysis with Google Places API (nearby amenities, POIs, reviews)
- Task planning and progress tracking with Deep Agents
- Human-in-the-loop property review
- Comprehensive property reports
- Clerk JWT authentication on all API endpoints
- Deployed on Vercel

## Tech Stack

**Backend:**
- Deep Agents (LangGraph) - Multi-agent orchestration
- FastAPI - API endpoint (Vercel serverless function)
- Vercel Postgres - State persistence
- Tavily API - Property search
- Google Places API - Location data and reviews

**Frontend:**
- Next.js (Pages Router)
- Clerk - Authentication with middleware route protection
- Tailwind CSS - Styling

## Setup

1. Install uv:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file from `.env.example` and add your API keys

4. Run locally:
```bash
# Backend
uv run uvicorn api.index:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

All endpoints require Clerk JWT authentication via `Authorization: Bearer <token>` header.

- `POST /api/invoke` - Start or continue agent conversation
- `POST /api/resume` - Resume agent after human-in-the-loop interrupt
- `GET /api/state` - Get current agent state for a thread
- `GET /health` - Health check endpoint

### Authentication Flow

1. User authenticates with Clerk on frontend
2. Clerk middleware protects `/agent` and `/profile` routes
3. Frontend obtains JWT token with `getToken()`
4. Token sent in Authorization header to API
5. FastAPI validates JWT and extracts user_id
6. Thread ID format: `{user_id}-{timestamp}`

## Project Structure

```
├── api/index.py          # FastAPI serverless function with all endpoints
├── src/
│   ├── agent.py          # Deep Agents (supervisor + sub-agents)
│   ├── tools.py          # Tavily, Google Places tools
│   ├── models.py         # Pydantic models (includes AgentRequest, ResumeRequest)
│   ├── prompts.py        # System prompts for agents
│   └── utils.py          # Helper functions
├── frontend/
│   ├── middleware.ts     # Clerk route protection
│   ├── src/pages/        # Next.js pages
│   └── components/       # React components
└── tests/                # Integration tests
```

## Deployment

### Environment Variables

Configure these environment variables in Vercel:
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude
- `CLERK_JWKS_URL` - Clerk JWKS URL for JWT validation
- `TAVILY_API_KEY` - Tavily API key for property search
- `MAPBOX_ACCESS_TOKEN` - Mapbox API token for location services
- `POSTGRES_URL` - Vercel Postgres connection string

### Deploy

```bash
vercel --prod
```

The `vercel.json` configuration automatically routes `/api/*` requests to the FastAPI serverless function.

## License

MIT

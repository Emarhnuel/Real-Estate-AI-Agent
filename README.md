# AI Real Estate Co-Pilot

An intelligent, conversational AI agent that automates property search and analysis using Deep Agents (LangGraph).



## Features

- Natural language property search with purpose-based filtering (rent, sale, shortlet)
- Automated property listing discovery with Tavily
- Purpose-specific search strategies for different property types
- Location analysis with Google Places API (nearby amenities, POIs, reviews)
- **Halloween Decorator** - AI-powered property decoration visualization with Gemini Vision
  - Analyze property images to identify decoration opportunities
  - Search e-commerce sites for Halloween decoration products
  - Generate AI-decorated images showing properties with Halloween themes
- Task planning and progress tracking with Deep Agents
- Human-in-the-loop property review
- Comprehensive property reports with PropertyReport data structure
- Clerk JWT authentication on all API endpoints
- Deployed on Vercel

## Tech Stack

**Backend:**
- Deep Agents (LangGraph) - Multi-agent orchestration
- FastAPI - API endpoint (Vercel serverless function)
- Vercel Postgres - State persistence
- Tavily API - Property search (rent, sale, shortlet)
- Google Places API - Location data and reviews
- Google Gemini API - Image analysis and AI-generated decoration visualizations

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
- `POST /api/resume` - Resume agent after human-in-the-loop interrupt (returns PropertyReport on completion)
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
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `CLERK_JWKS_URL` - Clerk JWKS URL for JWT validation
- `TAVILY_API_KEY` - Tavily API key for property search
- `GOOGLE_MAPS_API_KEY` - Google Maps API key for location services
- `GEMINI_API_KEY` - Google Gemini API key for image analysis and generation (optional, for Halloween Decorator feature)
- `POSTGRES_URL` - Vercel Postgres connection string

### Deploy

```bash
vercel --prod
```

The `vercel.json` configuration automatically routes `/api/*` requests to the FastAPI serverless function.

## License

MIT

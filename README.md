# AI Real Estate Co-Pilot

An intelligent, conversational AI agent that automates property search and analysis using Deep Agents (LangGraph).


## Features

- Natural language property search
- Automated property listing discovery with Tavily
- Location analysis with Google Places API (nearby amenities, POIs, reviews)
- Task planning and progress tracking with Deep Agents
- Human-in-the-loop property review
- Comprehensive property reports
- Clerk authentication
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
- Clerk - Authentication
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

## Project Structure

```
├── api/index.py          # FastAPI serverless function
├── src/
│   ├── agent.py          # Deep Agents (supervisor + sub-agents)
│   ├── tools.py          # Tavily, Google Places tools
│   ├── models.py         # Pydantic models
│   └── utils.py          # Helper functions
├── pages/                # Next.js pages
├── components/           # React components
└── tests/                # Integration tests
```

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## License

MIT

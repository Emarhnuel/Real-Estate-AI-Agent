# 🎃 AI Real Estate Co-Pilot 👻

> *"Find your dream home... if you dare!"*

An intelligent, conversational AI agent that automates property search and analysis using Deep Agents (LangGraph). Now with spooky Halloween decoration powers! 🦇

---

## ✨ Features

🔮 **Natural Language Search** - Speak your wishes and watch properties appear
- Purpose-based filtering (rent, sale, shortlet)
- Automated property listing discovery with Tavily
- Purpose-specific search strategies for different property types

📍 **Location Analysis** - Know what lurks nearby
- Google Places API integration
- Nearby amenities, POIs, and reviews
- Neighborhood insights

🎃 **Halloween Decorator** - Transform any property into a haunted mansion!
- AI-powered property decoration visualization with Gemini Vision
- Analyze property images to identify decoration opportunities
- Generate AI-decorated images showing properties with spooky Halloween themes
- Pumpkins, cobwebs, spooky lighting, and more!

📋 **Smart Workflow**
- Task planning and progress tracking with Deep Agents
- Human-in-the-loop property review
- Comprehensive property reports

🔐 **Secure** - Clerk JWT authentication on all API endpoints

---

## 🧙‍♂️ Tech Stack

**Backend (The Cauldron):**
- 🕸️ Deep Agents (LangGraph) - Multi-agent orchestration with FilesystemBackend
- ⚡ FastAPI - API endpoint
- 💾 MemorySaver - State persistence (development)
- 🔍 Tavily API - Property search (rent, sale, shortlet)
- 🗺️ Google Places API - Location data and reviews
- 👁️ Google Gemini API - Image analysis and AI-generated decoration visualizations

**Frontend (The Haunted House):**
- ⚛️ Next.js (Pages Router)
- 🔑 Clerk - Authentication with middleware route protection
- 🎨 Tailwind CSS - Styling

---

## 🕯️ Setup

1. **Summon uv:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Brew the dependencies:**
```bash
uv sync
```

3. **Create your spell book** (`.env` file from `.env.example`) and add your API keys

4. **(Optional) Enable LangSmith tracing** for monitoring your spirits:
```env
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=ai-real-estate-copilot
```

5. **Awaken the servers:**
```bash
# Backend
uv run uvicorn api.index:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🦴 API Endpoints

All endpoints require Clerk JWT authentication via `Authorization: Bearer <token>` header (except `/health`).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/invoke` | POST | Start or continue agent conversation |
| `/api/resume` | POST | Resume agent after human-in-the-loop interrupt |
| `/api/state` | POST | Get current agent state for a thread |
| `/api/decorated-image/{property_id}` | GET | Fetch Halloween-decorated image 🎃 |
| `/health` | GET | Health check (is the ghost still alive?) |

### 🔐 Authentication Flow

1. User authenticates with Clerk on frontend
2. Clerk middleware protects `/agent` and `/profile` routes
3. Frontend obtains JWT token with `getToken()`
4. Token sent in Authorization header to API
5. FastAPI validates JWT and extracts user_id
6. Thread ID format: `{user_id}-{timestamp}`

---

## 🏚️ Project Structure

```
├── api/index.py          # FastAPI serverless function 
├── src/
│   ├── agent.py          # Deep Agents (supervisor + sub-agents)
│   ├── tools.py          # Tavily, Google Places tools
│   ├── models.py         # Pydantic models
│   ├── prompts.py        # System prompts for agents
│   └── utils.py          # Helper functions
├── frontend/
│   ├── middleware.ts     # Clerk route protection
│   ├── src/pages/        # Next.js pages
│   └── components/       # React components
└── tests/                # Integration tests
```

---

## ⚰️ Environment Variables (Secret Ingredients)

- `OPENROUTER_API_KEY` - OpenRouter API key
- `CLERK_JWKS_URL` - Clerk JWKS URL for JWT validation
- `TAVILY_API_KEY` - Tavily API key for property search
- `GOOGLE_MAPS_API_KEY` - Google Maps API key
- `GEMINI_API_KEY` - Google Gemini API key (for Halloween Decorator 🎃)

---

## 📜 License

MIT

---

<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/jack-o-lantern_1f383.png" width="50" />
  <br>
  <em>Happy Haunting! 👻</em>
</p>

# 🏠 Property Gemini: AI-Powered Real Estate Intelligence

Welcome to **Property Gemini!** Built entirely upon the powerful reasoning and multimodal capabilities of **Amazon Nova 2** models via AWS Bedrock, this autonomous multi-agent system takes the guesswork out of property investment. 

Have you ever looked at a boring, outdated house listing and wondered, *"Could this be a modern masterpiece?"* Or looked at a neighborhood and asked, *"Is this actually a good area to invest in?"*

Property Gemini answers those questions instantly. We leverage advanced LLMs to analyze a property's location, assess its raw potential, and literally **reimagine its interior design** right before your eyes. It's like having a top-tier real estate agent, investment analyst, and interior designer working together for you around the clock.

---

## ✨ What it Does (The Magic)

Property Gemini features a team of specialized AI Agents acting as your personal real estate firm. When you input a location, the magic begins:

1. **The Search Agent (Data Gathering):** 
   Scours the web (via Tavily) for live, active real estate listings in your desired city or neighborhood, extracting raw listing data like prices, square footage, bedrooms, and property images.

2. **The Location Analyst Agent (Intelligence):** 
   Uses Google Places API to calculate a comprehensive "livability grade". It looks beyond the property lines right into the neighborhood, evaluating proximity to amenities, public transit, gyms, groceries, and airports to generate a definitive Location Score.

3. **The Interior Decorator Agent (Vision Analysis):** 
   Powered directly by `us.amazon.nova-lite-v1:0` via AWS Bedrock, this agent looks at the actual listing photos. It intelligently identifies room types (smartly ignoring exterior shots, facades, and gardens!) and assesses available spaces, existing furniture, and current color schemes. It then suggests a stunning "Modern Minimalist" design overhaul tailored exactly to the geometry of the room.

4. **The Render Agent (Generation):** 
   Takes the Interior Decorator's curated design suggestions and generates photorealistic mockup images of what the property *could* look like after renovations.

---

## 🛠️ How to Run It (Docker)

We've made running Property Gemini as easy as humanly possible using Docker Compose. A single command spins up both the React frontend and the FastAPI backend.

### Prerequisites
- Docker & Docker Compose installed on your machine.
- Your own API keys for the third-party services.

### Step 1: Setup API Keys
In the root directory of the project, create a file named `.env`. Depending on what agents you are running, you will need the appropriate keys:

```env
# AWS credentials for Amazon Nova (Bedrock) - Required for Vision & Reasoning
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# External Services
TAVILY_API_KEY=your_tavily_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Step 2: Spin it up!
Open your terminal in the project root and run this single magical command:

```bash
docker-compose up --build -d
```
*(Wait a few moments while Docker automatically downloads dependencies, builds the Node.js frontend, and sets up the Python backend containers.)*

### Step 3: Explore
Once the containers are running:
1. Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**
2. Click **Start Analysis** on the landing page.
3. Type in a location (e.g., "Austin TX" or "San Francisco") and watch the AI agents go to work!

*(Note: The FastAPI backend runs silently on `localhost:8000`, but you interact entirely through the sleek React frontend on port `3000`.)*

### Stopping the App
When you're done analyzing properties, simply run:
```bash
docker-compose down
```

---

## 🏗️ Architecture Stack

Property Gemini is built with scalability and performance in mind:

- **AI/LLM Framework:** Amazon Nova 2 (via AWS Bedrock) & LangChain
- **Backend Service:** Python, FastAPI, LangGraph (for multi-agent orchestration)
- **Frontend App:** React, Vite, TailwindCSS (for the beautiful design system), Framer Motion (for animations)
- **Deployment & Infra:** Docker & Docker Compose

***Stop guessing. Start knowing. Welcome to the future of real estate investing.***

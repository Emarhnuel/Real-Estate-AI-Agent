"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""


import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure LangSmith tracing (reads from env vars automatically)
# Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY in .env to enable
if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if os.getenv("LANGSMITH_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
    print(f"[INFO] LangSmith tracing enabled for project: {os.getenv('LANGSMITH_PROJECT', 'default')}")

from src.tools import (
    tavily_search_tool,
    tavily_extract_tool,
    google_places_geocode_tool,
    google_places_nearby_tool,
    present_properties_for_review_tool,
    submit_final_report_tool,
    analyze_property_images_tool,
    generate_decorated_image_tool,
    AGENT_DATA_DIR
)
from src.models import PropertyReport
from src.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Claude sonnet via OpenRouter
model1 = ChatOpenAI(
    model="x-ai/grok-4.1-fast",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

model = init_chat_model(model="gemini-3-pro-preview")

# Property Search Sub-Agent Configuration
property_search_agent = {
    "name": "property_search",
    "description": "Searches for property listings matching user criteria. Saves each property to /properties/ using write_file.",
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
    "tools": [tavily_search_tool, tavily_extract_tool],
    "model": model1
}

# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and nearby amenities. Saves analysis to /locations/ using write_file.",
    "system_prompt": LOCATION_ANALYSIS_SYSTEM_PROMPT,
    "tools": [google_places_geocode_tool, google_places_nearby_tool],
    "model": model1
}


# Halloween Decorator Sub-Agent Configuration
halloween_decorator_agent = {
    "name": "halloween_decorator",
    "description": "Analyzes property images and creates Halloween decoration plans with AI-generated decorated images. Searches for decoration products and provides budget estimates.",
    "system_prompt": HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    "tools": [analyze_property_images_tool, generate_decorated_image_tool],
    "model": model1
}



# Create Supervisor Agent
# Note: Deep Agents manages its own internal state (messages, todos, filesystem)
# Do NOT define a custom state schema - it conflicts with internal state management
checkpointer = MemorySaver()

# Ensure shared data directory exists (AGENT_DATA_DIR imported from tools.py)
os.makedirs(AGENT_DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(AGENT_DATA_DIR, "properties"), exist_ok=True)
os.makedirs(os.path.join(AGENT_DATA_DIR, "locations"), exist_ok=True)
os.makedirs(os.path.join(AGENT_DATA_DIR, "decorations"), exist_ok=True)

# Configure FilesystemBackend to use real disk instead of in-memory StateBackend
# This allows all agents (supervisor + subagents) to share the same filesystem
# root_dir must be an absolute path
filesystem_backend = FilesystemBackend(root_dir=AGENT_DATA_DIR)

supervisor_agent = create_deep_agent(
    model=model1,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    tools=[present_properties_for_review_tool, submit_final_report_tool],
    subagents=[property_search_agent, location_analysis_agent, halloween_decorator_agent],
    checkpointer=checkpointer,
    backend=filesystem_backend,
    interrupt_on={
        "present_properties_for_review_tool": True  # Pause before executing, allow approve/edit/reject
    }
)


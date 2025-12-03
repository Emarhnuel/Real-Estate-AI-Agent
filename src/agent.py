"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""


import os
from typing import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.middleware import ModelFallbackMiddleware, ModelRetryMiddleware
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
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
    generate_decorated_image_tool
)
from src.models import PropertyReport
from src.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

# =============================================================================
# MODEL CONFIGURATION WITH FALLBACK
# =============================================================================

# Primary model: Grok via OpenRouter (free tier)
primary_model = ChatOpenAI(
    model="x-ai/grok-4.1-fast:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    timeout=120,
)

# Fallback model 1: Gemini (if you have GEMINI_API_KEY)
fallback_model_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    timeout=120,
) if os.getenv("GEMINI_API_KEY") else None

# Fallback model 2: Another free OpenRouter model
fallback_model_llama = ChatOpenAI(
    model="meta-llama/llama-3.3-8b-instruct:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    timeout=120,
) if os.getenv("OPENROUTER_API_KEY") else None

# Build middleware list
middleware_list = [
    # Retry on transient failures (timeouts, rate limits)
    ModelRetryMiddleware(
        max_retries=2,
        backoff_factor=2.0,
        initial_delay=1.0,
        on_failure="continue",  # Return error message instead of crashing
    ),
]

# Add fallback middleware with available models
fallback_models = []
if fallback_model_gemini:
    fallback_models.append(fallback_model_gemini)
if fallback_model_llama:
    fallback_models.append(fallback_model_llama)

if fallback_models:
    middleware_list.append(ModelFallbackMiddleware(*fallback_models))
    print(f"[INFO] Model fallback enabled with {len(fallback_models)} backup model(s)")

# Use primary model for all agents
model1 = primary_model


# Property Search Sub-Agent Configuration

property_search_agent = {
    "name": "property_search",
    "description": "Searches for property listings matching user criteria using web search. Returns summary of found properties with data saved to filesystem.",
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
    "tools": [tavily_search_tool, tavily_extract_tool],
    "model": model1
}



# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and finds nearby points of interest. Evaluates location pros and cons based on amenities, transportation, and services.",
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



# Supervisor Agent State Schema
class SupervisorState(TypedDict):
    """State schema for the supervisor agent."""
    messages: Annotated[list, add_messages]
    todos: list[dict]
    search_criteria: dict
    approved_properties: list[str]
    filesystem: dict
    # structured_response will be automatically added by LangChain when response_format is set


# Create Supervisor Agent
checkpointer = MemorySaver()


# Configure StateBackend for all paths - ephemeral per-thread storage
# Each new thread_id gets a fresh filesystem, preventing old search data from persisting
composite_backend = lambda rt: StateBackend(rt)

supervisor_agent = create_deep_agent(
    model=model1,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    tools=[present_properties_for_review_tool, submit_final_report_tool],
    subagents=[property_search_agent, location_analysis_agent, halloween_decorator_agent],
    checkpointer=checkpointer,
    backend=composite_backend,
    middleware=middleware_list,  # Add retry + fallback middleware
    interrupt_on={
        "present_properties_for_review_tool": True  # Pause before executing, allow approve/edit/reject
    }
)


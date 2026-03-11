"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""

import os
from pathlib import Path
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, CompositeBackend, StoreBackend
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
    browser_use_extract_tool,
    google_places_geocode_tool,
    google_places_nearby_tool,
    present_properties_for_review_tool,
    analyze_property_images_tool,
    generate_decorated_image_tool,
)
from src.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    INTERIOR_DECORATOR_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Amazon Bedrock - Main model for all agents
model1 = ChatBedrockConverse( 
    model_id="us.amazon.nova-2-lite-v1:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    temperature=0.0,
    max_tokens=40960,
)

# =============================================================================
# BACKEND CONFIGURATION
# =============================================================================

checkpointer = MemorySaver()

# Agent data directory - all sub-agent files land here on actual disk
AGENT_DATA_DIR = Path("agent_data")
AGENT_DATA_DIR.mkdir(exist_ok=True)

# FilesystemBackend: writes real files to ./agent_data on disk.
# virtual_mode=True prevents path traversal (../ or ~/ escapes).
# CompositeBackend routes /memories/ to StoreBackend for cross-session user preferences.
_fs_backend = FilesystemBackend(root_dir=str(AGENT_DATA_DIR), virtual_mode=True)

def make_backend(runtime):
    return CompositeBackend(
        default=_fs_backend,
        routes={
            "/memories/": StoreBackend(runtime),
        }
    )


# =============================================================================
# AGENT FACTORY
# =============================================================================

# Property Search Sub-Agent Configuration
property_search_agent = {
    "name": "property_search",
    "description": (
        "Searches for property listings matching user criteria. "
        "Extracts detailed property data from listing pages. "
        "Saves properties and asks for human review."
    ),
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT, 
    "tools": [tavily_search_tool, browser_use_extract_tool, present_properties_for_review_tool],
    "model": model1,
    "interrupt_on": {"present_properties_for_review_tool": True},
}

# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and nearby amenities. Saves analysis to /locations/ using write_file.",
    "system_prompt": LOCATION_ANALYSIS_SYSTEM_PROMPT,
    "tools": [google_places_geocode_tool, google_places_nearby_tool],
    "model": model1
}

# Interior Decorator Sub-Agent Configuration
interior_decorator_agent = {
    "name": "interior_decorator",
    "description": "Analyzes property images and creates interior decoration plans with AI-generated decorated images. Searches for decoration products and provides budget estimates.",
    "system_prompt": INTERIOR_DECORATOR_SYSTEM_PROMPT,
    "tools": [analyze_property_images_tool, generate_decorated_image_tool],
    "model": model1
}
 
# Create the supervisor agent
supervisor = create_deep_agent(
    model=model1,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    subagents=[property_search_agent, location_analysis_agent, interior_decorator_agent],
    tools=[],
    checkpointer=checkpointer,
    backend=make_backend,
    store=InMemoryStore(),  # For local dev; swap for PostgresStore in production
)

print("[INFO] Supervisor agent created successfully")

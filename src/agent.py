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
from langchain_core.messages import AIMessage
from langgraph.types import Command
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


model2 = ChatBedrockConverse( 
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    temperature=0.0,
    max_tokens=63000,
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


# Interior Decorator Sub-Agent Configuration
# To prevent infinite thought loops, we apply a strict step limit via an after_model hook.
def interior_decorator_step_limiter(state, response):
    """Custom middleware to force stop if the agent loops without tools too many times or exceeds strict tool call limits."""
    messages = state.get("messages", []) + [response]
    
    # 1. Check for consecutive "thought" messages without actual tool calls
    ai_consecutive_count = 0
    for msg in reversed(messages):
        if getattr(msg, "type", "") == "human":
            break
        if getattr(msg, "type", "") == "ai":
            # If it has tool calls, it's actually doing work, not just looping thoughts
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                continue
            ai_consecutive_count += 1
            
    # If the LLM has pontificated 4 times in a row without making progress, kill it
    if ai_consecutive_count >= 4:
        print("[WARNING] Interior Decorator hit thought loop limit. Forcing stop.")
        from langgraph.types import Command
        return Command(goto="__end__")

    # 2. Check for hard limits on specific tool executions over the entire thread
    analyze_calls = 0
    generate_calls = 0
    
    for msg in messages:
        if getattr(msg, "type", "") == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.get("name", "")
                if name == "analyze_property_images_tool":
                    analyze_calls += 1
                elif name == "generate_decorated_image_tool":
                    generate_calls += 1

    # Apply limits: 6 for analyze, 4 for generate
    if analyze_calls > 6 or generate_calls > 4:
        print(f"[WARNING] Interior Decorator tool limits reached ({analyze_calls}/6 analyze, {generate_calls}/4 generate). Forcing stop.")
        from langgraph.types import Command
        return Command(goto="__end__")
        
    # Return the normal model response if limits are not reached
    return {"messages": [response]}




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


interior_decorator_agent = {
    "name": "interior_decorator",
    "description": "Analyzes property images and creates interior decoration plans with AI-generated decorated images. Searches for decoration products and provides budget estimates.",
    "system_prompt": INTERIOR_DECORATOR_SYSTEM_PROMPT,
    "tools": [analyze_property_images_tool, generate_decorated_image_tool],
    "model": model2,
    "hooks": {
        "after_model": [interior_decorator_step_limiter]
    }
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

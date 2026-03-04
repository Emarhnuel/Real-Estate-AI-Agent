"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""

import os
from langchain_amazon_nova import ChatAmazonNova
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
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
    # tavily_search_tool,  # Replaced by Nova Web Grounding
    # tavily_extract_tool,  # Replaced by Nova Web Grounding
    google_places_geocode_tool,
    google_places_nearby_tool,
    present_properties_for_review_tool,
    submit_final_report_tool,
    analyze_property_images_tool,
    generate_decorated_image_tool,
)
from src.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Amazon Nova - Main model for supervisor (most capable)
model = ChatAmazonNova(
    model="nova-premier-v1",
    temperature=0.7,
    max_tokens=4096,
)

# Amazon Nova - Lighter model for sub-agents (faster, cheaper for focused tasks)
model1 = ChatAmazonNova(
    model="nova-2-lite-v1",
    temperature=0.7,
    max_tokens=4096,
)

# Amazon Nova - Model with Web Grounding for property search (replaces Tavily)
model_with_grounding = ChatAmazonNova(
    model="nova-2-lite-v1",
    temperature=0.7,
    max_tokens=4096,
    system_tools=["nova_grounding"],
)

# =============================================================================
# BACKEND CONFIGURATION
# =============================================================================

checkpointer = MemorySaver()

# CompositeBackend: hybrid storage for ephemeral + persistent data
# - StateBackend (default): ephemeral per-thread storage for /properties/, /locations/, /decorations/
#   → Automatically cleaned up when the thread ends. No data leaks between sessions.
# - StoreBackend (/memories/): persistent cross-thread storage for user preferences
#   → Remembers user preferences across sessions (e.g., "I prefer 3-bedroom apartments")
def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime),
        }
    )


# =============================================================================
# MCP CLIENT & AGENT FACTORY (async)
# =============================================================================

# Global reference - set by create_supervisor_agent() at startup
supervisor = None
mcp_client = None


async def create_supervisor_agent():
    """
    Async factory that initializes the MCP client, gets browser tools,
    and creates the supervisor agent with all sub-agents.

    Must be called once at app startup (e.g., in FastAPI lifespan).
    """
    global supervisor, mcp_client

    # Initialize Browser Use MCP client (cloud-hosted)
    mcp_client = MultiServerMCPClient(
        {
            "browser-use": {
                "transport": "http",
                "url": "https://api.browser-use.com/mcp",
                "headers": {
                    "X-Browser-Use-API-Key": os.getenv("BROWSER_USE_API_KEY", ""),
                },
            }
        }
    )

    # Get browser automation tools from MCP server
    browser_tools = await mcp_client.get_tools()
    print(f"[INFO] Loaded {len(browser_tools)} Browser Use MCP tools")

    # Property Search Sub-Agent Configuration
    # Uses Nova Web Grounding for search + Browser Use MCP for scraping
    property_search_agent = {
        "name": "property_search",
        "description": (
            "Searches for property listings matching user criteria using web grounding. "
            "Uses browser automation to extract detailed property data from listing pages. "
            "Saves properties and asks for human review."
        ),
        "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
        "tools": [present_properties_for_review_tool] + browser_tools,
        "model": model_with_grounding,
        "interrupt_on": {
            "present_properties_for_review_tool": {"allowed_decisions": ["approve", "edit", "reject"]}
        }
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

    # Create the supervisor agent
    supervisor = create_deep_agent(
        model=model,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        subagents=[property_search_agent, location_analysis_agent, halloween_decorator_agent],
        tools=[submit_final_report_tool],
        checkpointer=checkpointer,
        backend=make_backend,
        store=InMemoryStore(),  # For local dev; swap for PostgresStore in production
    )

    print("[INFO] Supervisor agent created successfully with Browser Use MCP tools")
    return supervisor


async def shutdown_mcp_client():
    """Cleanup MCP client connections on shutdown."""
    global mcp_client
    mcp_client = None

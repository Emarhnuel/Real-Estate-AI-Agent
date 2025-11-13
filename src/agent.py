"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tools import (
    tavily_search_tool,
    mapbox_geocode_tool,
    mapbox_nearby_tool,
    present_properties_for_review_tool
)
from models import PropertyReport
from prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

# Property Search Sub-Agent Configuration

property_search_agent = {
    "name": "property_search",
    "description": "Searches for property listings matching user criteria using web search. Returns summary of found properties with data saved to filesystem.",
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
    "tools": [tavily_search_tool],
    "model": "gpt-4o"
}


# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and finds nearby points of interest. Evaluates location pros and cons based on amenities, transportation, and services.",
    "system_prompt": LOCATION_ANALYSIS_SYSTEM_PROMPT,
    "tools": [mapbox_geocode_tool, mapbox_nearby_tool],
    "model": "gpt-4o"
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

supervisor_agent = create_deep_agent(
    model="gpt-4o",
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    tools=[present_properties_for_review_tool],
    subagents=[property_search_agent, location_analysis_agent],
    checkpointer=checkpointer,
    response_format=PropertyReport
)


if __name__ == "__main__":
    # Test the agent with a sample query
    config = {"configurable": {"thread_id": "test-agent-001"}}
    
    result = supervisor_agent.invoke(
        {"messages": [{"role": "user", "content": "I want a 2 bedroom property for rent in Ojodu lagos"}]},
        config=config
    )
    
    # Print the agent's response
    print(result["messages"][-1].content)
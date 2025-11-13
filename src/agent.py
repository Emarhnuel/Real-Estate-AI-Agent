"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""

from typing import TypedDict, Annotated
from langchain.chat_models import init_chat_model
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
    present_properties_for_review_tool,
    submit_final_report_tool
)
from models import PropertyReport
from prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)

model = init_chat_model(
    model="gpt-5-nano-2025-08-07",
)

# Property Search Sub-Agent Configuration

property_search_agent = {
    "name": "property_search",
    "description": "Searches for property listings matching user criteria using web search. Returns summary of found properties with data saved to filesystem.",
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
    "tools": [tavily_search_tool],
    "model": model
}


# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and finds nearby points of interest. Evaluates location pros and cons based on amenities, transportation, and services.",
    "system_prompt": LOCATION_ANALYSIS_SYSTEM_PROMPT,
    "tools": [mapbox_geocode_tool, mapbox_nearby_tool],
    "model": model 
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
    model=model,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    tools=[present_properties_for_review_tool, submit_final_report_tool],
    subagents=[property_search_agent, location_analysis_agent],
    checkpointer=checkpointer,
    # response_format=PropertyReport
)


if __name__ == "__main__":
    # Unique ID for the conversation thread
    config = {"configurable": {"thread_id": "test-agent-002"}}
    
    # List to store the conversation history
    messages = []

    while True:
        # Get input from the user
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting conversation.")
            break

        # Add the new user message to the history
        messages.append({"role": "user", "content": user_input})

        # Invoke the agent with the entire conversation history
        result = supervisor_agent.invoke(
            {"messages": messages},
            config=config
        )
        
        # The agent's response is the last message in the list
        agent_response = result["messages"][-1]
        
        # Add the agent's response to the history
        messages.append(agent_response)
        
        # Check if the final tool was called to display the report
        if agent_response.tool_calls and any(tc['name'] == 'submit_final_report_tool' for tc in agent_response.tool_calls):
            print("Agent has submitted the final report!")
            # In a real app, you would now parse the tool call args to get the report
            final_report_data = next(tc['args']['report'] for tc in agent_response.tool_calls if tc['name'] == 'submit_final_report_tool')
            print("\n--- FINAL REPORT ---")
            print(final_report_data)
            print("--------------------")
        else:
            # Print the agent's conversational response
            print(f"Agent: {agent_response.content}")
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
    from langgraph.types import Command
    
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
        
        # Check if there's an interrupt (human-in-the-loop)
        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"]
            print("\n" + "="*60)
            print("PROPERTY REVIEW - Please approve or reject each property")
            print("="*60)
            
            # Display properties for review
            # interrupt_data is a list of interrupt payloads
            if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
                # Get the first interrupt (should be the property review)
                interrupt_payload = interrupt_data[0]
                
                # The payload has a 'value' key containing our interrupt data
                if "value" in interrupt_payload:
                    interrupt_value = interrupt_payload["value"]
                    properties = interrupt_value.get("properties", [])
                    
                    if not properties:
                        print("No properties to review.")
                        continue
                    
                    print(f"\nFound {len(properties)} properties for your review:\n")
                    
                    for idx, prop in enumerate(properties, 1):
                        print(f"\n--- Property {idx} ---")
                        print(f"ID: {prop.get('id', 'N/A')}")
                        print(f"Address: {prop.get('address', 'N/A')}")
                        print(f"Price: ₦{prop.get('price', 0):,.0f}/year")
                        print(f"Bedrooms: {prop.get('bedrooms', 'N/A')}")
                        print(f"Bathrooms: {prop.get('bathrooms', 'N/A')}")
                        if prop.get('image_urls'):
                            print(f"Images: {len(prop['image_urls'])} available")
                        print("-" * 40)
                    
                    # Collect user decisions
                    print("\nEnter property IDs to APPROVE (comma-separated, e.g., property_001,property_003):")
                    print("Or type 'all' to approve all, or 'none' to reject all")
                    approval_input = input("Approve: ").strip()
                    
                    if approval_input.lower() == "all":
                        approved = [p["id"] for p in properties]
                        rejected = []
                    elif approval_input.lower() == "none":
                        approved = []
                        rejected = [p["id"] for p in properties]
                    else:
                        approved = [pid.strip() for pid in approval_input.split(",") if pid.strip()]
                        all_ids = [p["id"] for p in properties]
                        rejected = [pid for pid in all_ids if pid not in approved]
                    
                    print(f"\n✓ Approved: {len(approved)} properties")
                    print(f"✗ Rejected: {len(rejected)} properties")
                    
                    # Resume with the approval decisions
                    resume_data = {
                        "approved": approved,
                        "rejected": rejected
                    }
                    
                    print("\nResuming agent with your decisions...")
                    
                    # Resume the agent with Command
                    result = supervisor_agent.invoke(
                        Command(resume=resume_data),
                        config=config
                    )
            else:
                print("Unexpected interrupt format. Continuing...")
                continue
        
        # Get the agent's response
        if "messages" in result and len(result["messages"]) > 0:
            agent_response = result["messages"][-1]
            
            # Add the agent's response to the history
            messages.append(agent_response)
            
            # Check if the final tool was called to display the report
            if hasattr(agent_response, 'tool_calls') and agent_response.tool_calls:
                if any(tc['name'] == 'submit_final_report_tool' for tc in agent_response.tool_calls):
                    print("\n" + "="*60)
                    print("FINAL REPORT SUBMITTED")
                    print("="*60)
                    # In a real app, you would now parse the tool call args to get the report
                    final_report_data = next(tc['args']['report'] for tc in agent_response.tool_calls if tc['name'] == 'submit_final_report_tool')
                    print(final_report_data)
                    print("="*60)
            
            # Print the agent's conversational response
            if hasattr(agent_response, 'content') and agent_response.content:
                print(f"\nAgent: {agent_response.content}")
        else:
            print("\nAgent: [No response]")
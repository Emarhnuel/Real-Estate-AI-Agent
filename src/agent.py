"""
Agent configurations for AI Real Estate Co-Pilot.

This module defines the supervisor agent and sub-agents for property search
and location analysis using the Deep Agents framework.
"""

from typing import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.tools import (
    tavily_search_tool,
    tavily_extract_tool,
    google_places_geocode_tool,
    google_places_nearby_tool,
    present_properties_for_review_tool,
    submit_final_report_tool,
    analyze_property_images_tool,
    search_halloween_decorations_tool,
    generate_decorated_image_tool
)
from src.models import PropertyReport
from src.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    LOCATION_ANALYSIS_SYSTEM_PROMPT,
    HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT
)


model = init_chat_model(
    model="gpt-5-mini-2025-08-07",
)

# Property Search Sub-Agent Configuration

property_search_agent = {
    "name": "property_search",
    "description": "Searches for property listings matching user criteria using web search. Returns summary of found properties with data saved to filesystem.",
    "system_prompt": PROPERTY_SEARCH_SYSTEM_PROMPT,
    "tools": [tavily_search_tool, tavily_extract_tool],
    "model": model
}


# Location Analysis Sub-Agent Configuration
location_analysis_agent = {
    "name": "location_analysis",
    "description": "Analyzes property locations and finds nearby points of interest. Evaluates location pros and cons based on amenities, transportation, and services.",
    "system_prompt": LOCATION_ANALYSIS_SYSTEM_PROMPT,
    "tools": [google_places_geocode_tool, google_places_nearby_tool],
    "model": model 
}


# Halloween Decorator Sub-Agent Configuration
halloween_decorator_agent = {
    "name": "halloween_decorator",
    "description": "Analyzes property images and creates Halloween decoration plans with AI-generated decorated images. Searches for decoration products and provides budget estimates.",
    "system_prompt": HALLOWEEN_DECORATOR_SYSTEM_PROMPT,
    "tools": [analyze_property_images_tool, search_halloween_decorations_tool, generate_decorated_image_tool],
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
    subagents=[property_search_agent, location_analysis_agent, halloween_decorator_agent],
    checkpointer=checkpointer
)


# if __name__ == "__main__":
#     from langgraph.types import Command
    
#     # Unique ID for the conversation thread
#     config = {"configurable": {"thread_id": "test-agent-004"}}

#     print("Real Estate AI Agent - Type 'exit' or 'quit' to end the conversation\n")

#     while True:
#         # Get input from the user
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Exiting conversation.")
#             break

#         # Invoke the agent with the user message
#         result = supervisor_agent.invoke(
#             {"messages": [{"role": "user", "content": user_input}]},
#             config=config
#         )
        
#         # Check for interrupt (human-in-the-loop)
#         if "__interrupt__" in result:
#             print("\n" + "="*60)
#             print("PROPERTY REVIEW - Please approve or reject properties")
#             print("="*60)
            
#             # Extract properties from interrupt payload
#             interrupt_data = result["__interrupt__"]
#             properties = []
            
#             if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
#                 # Get the interrupt object
#                 interrupt_obj = interrupt_data[0]
                
#                 # Access the value attribute (not dict key)
#                 if hasattr(interrupt_obj, 'value'):
#                     interrupt_value = interrupt_obj.value
#                     properties = interrupt_value.get("properties", [])
            
#             if not properties:
#                 print("\nNo properties found in interrupt. Skipping review.")
#                 continue
            
#             # Display each property with details
#             print(f"\nFound {len(properties)} properties:\n")
            
#             for idx, prop in enumerate(properties, 1):
#                 print(f"--- Property {idx} ---")
#                 print(f"ID: {prop.get('id', 'N/A')}")
#                 print(f"Address: {prop.get('address', 'N/A')}")
#                 print(f"Price: ₦{prop.get('price', 0):,.0f}/year")
#                 print(f"Bedrooms: {prop.get('bedrooms', 'N/A')}")
#                 print(f"Bathrooms: {prop.get('bathrooms', 'N/A')}")
                
#                 # Display listing URL
#                 listing_url = prop.get('listing_url', 'N/A')
#                 print(f"Listing: {listing_url}")
                
#                 # Display image URLs if available
#                 image_urls = prop.get('image_urls', [])
#                 if image_urls:
#                     print(f"Images: {len(image_urls)} available")
#                     for img_idx, img_url in enumerate(image_urls, 1):
#                         print(f"  Image {img_idx}: {img_url}")
#                 else:
#                     print("Images: None available")
                
#                 print()
            
#             # Prompt for approval
#             print("Enter property IDs to APPROVE (comma-separated):")
#             print("Example: property_001,property_002")
#             print("Or type 'all' to approve all properties\n")
            
#             approval_input = input("Approve: ").strip()
            
#             # Parse approvals
#             if approval_input.lower() == "all":
#                 approved = [p["id"] for p in properties]
#                 rejected = []
#             else:
#                 approved = [pid.strip() for pid in approval_input.split(",") if pid.strip()]
#                 all_ids = [p["id"] for p in properties]
#                 rejected = [pid for pid in all_ids if pid not in approved]
            
#             print(f"\n✓ Approved: {len(approved)} properties")
#             print(f"✗ Rejected: {len(rejected)} properties\n")
            
#             # Resume with the approval decisions
#             resume_data = {
#                 "approved": approved,
#                 "rejected": rejected
#             }
            
#             # Resume the agent
#             result = supervisor_agent.invoke(
#                 Command(resume=resume_data),
#                 config=config
#             )
        
#         # Get the agent's response
#         if "messages" in result and len(result["messages"]) > 0:
#             agent_response = result["messages"][-1]
            
#             # Print the agent's conversational response
#             if hasattr(agent_response, 'content') and agent_response.content:
#                 print(f"\nAgent: {agent_response.content}\n")
#             else:
#                 print("\nAgent: [Processing...]\n")
#         else:
#             print("\nAgent: [No response]\n")
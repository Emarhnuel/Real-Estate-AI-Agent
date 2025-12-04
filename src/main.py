"""
FastAPI server for AI Real Estate Co-Pilot.

This module provides API endpoints for agent interaction with Clerk authentication.
All endpoints are protected and require valid JWT tokens from authenticated users.
"""

import os
import json
import ast
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from langgraph.types import Command

# Import agent and models
import sys
sys.path.append('..')
from src.agent import supervisor_agent
from src.models import AgentRequest, ResumeRequest, StateRequest


def extract_final_report(result: dict) -> Optional[dict]:
    """Extract the final report from agent result messages."""
    if "messages" not in result:
        return None
    
    for msg in reversed(result["messages"]):
        content = getattr(msg, "content", None)
        if content is None and isinstance(msg, dict):
            content = msg.get("content")
        
        if content is None:
            continue
        
        # Debug: log content type for each message
        print(f"[DEBUG extract] type={type(msg).__name__}, content_type={type(content).__name__}")
        
        # Parse content if it's a JSON string
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Check if this is a report response (dict with "report" key)
        if isinstance(content, dict) and "report" in content:
            print(f"[DEBUG extract] Found report!")
            return content["report"]
    
    return None

app = FastAPI(title="AI Real Estate Co-Pilot API")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk authentication configuration
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


@app.post("/api/invoke")
def invoke_agent(
    request: AgentRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """
    Start a new agent conversation or continue an existing one.
    
    Args:
        request: AgentRequest containing messages and timestamp
        creds: Clerk authentication credentials (injected by dependency)
        
    Returns:
        Agent execution result including messages, state, and any interrupts
    """
    # Extract user ID from JWT token
    user_id = creds.decoded["sub"]
    
    # Generate unique thread ID for this user session
    thread_id = f"{user_id}-{request.timestamp}"
    
    # Configure agent with thread ID for state persistence
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Invoke the supervisor agent with user messages
        result = supervisor_agent.invoke(
            {"messages": request.messages},
            config=config
        )
        
        # Extract final report if present
        report = extract_final_report(result)
        if report:
            result["structured_response"] = report
        
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] Agent invocation failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")


@app.post("/api/resume")
def resume_agent(
    request: ResumeRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """
    Resume agent execution after a human-in-the-loop interrupt.
    
    Uses Deep Agents HITL format: Command(resume={"decisions": [{"type": "approve"}]})
    
    Args:
        request: ResumeRequest containing thread_id and approved_properties
        creds: Clerk authentication credentials (injected by dependency)
        
    Returns:
        Agent execution result after resuming from interrupt
    """
    # Extract user ID from JWT token for verification
    user_id = creds.decoded["sub"]
    
    # Verify the thread_id belongs to this user (security check)
    if not request.thread_id.startswith(user_id):
        raise HTTPException(status_code=403, detail="Thread ID does not belong to authenticated user")
    
    # Configure agent with the thread ID to resume
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        approved_ids = request.approved_properties or []
        
        print(f"[DEBUG] Resuming with thread_id: {request.thread_id}")
        print(f"[DEBUG] Approved properties: {approved_ids}")
        
        # Deep Agents HITL format per docs:
        # - approve: {"type": "approve"}
        # - reject: {"type": "reject"}
        # - edit: {"type": "edit", "edited_action": {"name": "tool_name", "args": {...}}}
        
        if not approved_ids:
            # User rejected all properties
            resume_data = {
                "decisions": [{"type": "reject"}]
            }
        else:
            # User approved some properties - use edit to pass only approved ones
            resume_data = {
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "present_properties_for_review_tool",
                            "args": {
                                "properties": [{"id": pid} for pid in approved_ids]
                            }
                        }
                    }
                ]
            }
        
        print(f"[DEBUG] Resume data (HITL format): {resume_data}")
        
        # Resume agent execution with Command
        result = supervisor_agent.invoke(
            Command(resume=resume_data),
            config=config
        )
        
        print(f"[DEBUG] Resume successful, result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
        
        # Debug: Print message types and content snippets
        if "messages" in result:
            print(f"[DEBUG] Number of messages: {len(result['messages'])}")
            for i, msg in enumerate(result["messages"][-5:]):  # Last 5 messages
                msg_type = type(msg).__name__
                content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
                content_preview = str(content)[:200] if content else "None"
                print(f"[DEBUG] Message {i}: type={msg_type}, content_preview={content_preview}")
        
        # Extract final report if present
        report = extract_final_report(result)
        if report:
            result["structured_response"] = report
            print(f"[DEBUG] Extracted structured_response from final report")
        else:
            print(f"[DEBUG] No final report found in messages")
        
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] Agent resume failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Agent resume failed: {str(e)}")


@app.post("/api/state")
def get_state(
    request: StateRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """Get the current state of an agent conversation."""
    user_id = creds.decoded["sub"]
    thread_id = request.thread_id
    
    if not thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required")
    
    print(f"[DEBUG /api/state] user_id: '{user_id}', thread_id: '{thread_id}'")
    
    # Verify the thread_id belongs to this user
    if not thread_id.startswith(user_id):
        raise HTTPException(status_code=403, detail="Thread ID does not belong to authenticated user")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        state = supervisor_agent.get_state(config)
        state_values = state.values if state else {}
        
        # Try to extract final report from state messages
        report = extract_final_report(state_values)
        if report:
            state_values["structured_response"] = report
        
        return state_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve state: {str(e)}")


@app.get("/api/decorated-image/{property_id}")
def get_decorated_image(
    property_id: str,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """
    Get decorated image data from external disk storage.
    
    Args:
        property_id: Property ID (e.g., "property_001")
        creds: Clerk authentication credentials (injected by dependency)
        
    Returns:
        Decorated image data including base64-encoded image
    """
    import json
    from pathlib import Path
    
    # Build path to decorated image file
    file_path = Path("decorated_images") / f"{property_id}_halloween.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Decorated image not found for {property_id}")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read decorated image: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "ai-real-estate-copilot"}
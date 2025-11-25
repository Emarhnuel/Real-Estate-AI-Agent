"""
FastAPI server for AI Real Estate Co-Pilot.

This module provides API endpoints for agent interaction with Clerk authentication.
All endpoints are protected and require valid JWT tokens from authenticated users.
"""


import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from langgraph.types import Command

# Import agent and models
import sys
sys.path.append('..')
from src.agent import supervisor_agent
from src.models import AgentRequest, ResumeRequest

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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")


@app.post("/api/resume")
def resume_agent(
    request: ResumeRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """
    Resume agent execution after a human-in-the-loop interrupt.
    
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
        # Prepare resume data with user's property approvals
        resume_data = {
            "approved": request.approved_properties or [],
            "rejected": []  # Can be extended to include rejected property IDs
        }
        
        print(f"[DEBUG] Resuming with thread_id: {request.thread_id}")
        print(f"[DEBUG] Resume data: {resume_data}")
        
        # Resume agent execution with Command
        result = supervisor_agent.invoke(
            Command(resume=resume_data),
            config=config
        )
        
        print(f"[DEBUG] Resume successful, result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] Agent resume failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Agent resume failed: {str(e)}")


@app.get("/api/state")
def get_state(
    thread_id: str,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """
    Get the current state of an agent conversation.
    
    Args:
        thread_id: The thread ID to retrieve state for
        creds: Clerk authentication credentials (injected by dependency)
        
    Returns:
        Current agent state including messages, todos, and filesystem
    """
    # Extract user ID from JWT token for verification
    user_id = creds.decoded["sub"]
    
    # Verify the thread_id belongs to this user (security check)
    if not thread_id.startswith(user_id):
        raise HTTPException(status_code=403, detail="Thread ID does not belong to authenticated user")
    
    # Configure agent with thread ID
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Get current state from checkpointer
        state = supervisor_agent.get_state(config)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve state: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "ai-real-estate-copilot"}

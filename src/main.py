"""
FastAPI server for AI Real Estate Co-Pilot.

Handles agent invocation, human-in-the-loop interrupts, and final report delivery.
Protected by Clerk authentication.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from langgraph.types import Command
from dotenv import load_dotenv

from src.agent import supervisor_agent
from src.models import AgentRequest, ResumeRequest, StateRequest

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="AI Real Estate Co-Pilot API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk authentication
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


def validate_thread_ownership(thread_id: str, user_id: str) -> None:
    """Ensure the thread belongs to the authenticated user."""
    if not thread_id.startswith(f"{user_id}-"):
        raise HTTPException(status_code=403, detail="Access denied to this thread")


def extract_final_report(state: dict, thread_id: str) -> dict | None:
    """Extract report from submit_final_report_tool or build from filesystem as fallback."""
    messages = state.get("messages", [])
    
    # First, try to find submit_final_report_tool response
    for msg in reversed(messages):
        if hasattr(msg, "name") and msg.name == "submit_final_report_tool":
            content = msg.content
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    continue
            if isinstance(content, dict) and content.get("status") == "success":
                # Tool was called - build full report from filesystem using the summary
                return build_report_from_filesystem(thread_id, content)
    
    # Fallback: Check if all todos are complete but tool wasn't called
    todos = state.get("todos", [])
    all_complete = todos and all(t.get("status") == "completed" for t in todos)
    if all_complete:
        logger.info("[REPORT] Todos complete but tool not called - building from filesystem")
        return build_report_from_filesystem(thread_id, None)
    
    return None


def build_report_from_filesystem(thread_id: str, tool_response: dict | None) -> dict | None:
    """Build complete PropertyReport from filesystem data."""
    from src.agent import supervisor_agent
    from datetime import datetime
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Get the agent's filesystem state
        state_snapshot = supervisor_agent.get_state(config)
        if not state_snapshot or not state_snapshot.values:
            return None
        
        filesystem = state_snapshot.values.get("filesystem", {})
        
        # Read properties from /properties/
        properties = []
        properties_dir = filesystem.get("properties", {})
        for filename, content in properties_dir.items():
            if filename.endswith(".json"):
                try:
                    prop_data = json.loads(content) if isinstance(content, str) else content
                    properties.append(prop_data)
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Read location analyses from /locations/
        location_analyses = {}
        locations_dir = filesystem.get("locations", {})
        for filename, content in locations_dir.items():
            if filename.endswith(".json"):
                try:
                    loc_data = json.loads(content) if isinstance(content, str) else content
                    prop_id = loc_data.get("property_id", filename.replace(".json", ""))
                    location_analyses[prop_id] = loc_data
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Read decoration metadata from /decorations/
        decorated_images = {}
        decorations_dir = filesystem.get("decorations", {})
        for filename, content in decorations_dir.items():
            if filename.endswith(".json"):
                try:
                    dec_data = json.loads(content) if isinstance(content, str) else content
                    prop_id = dec_data.get("property_id", "")
                    external_path = dec_data.get("external_disk_path", "")
                    if prop_id:
                        decorated_images[prop_id] = external_path
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Build search criteria from tool response or defaults
        if tool_response:
            search_criteria = tool_response.get("search_criteria", {})
        else:
            search_criteria = {"location": "Unknown", "max_price": 0, "min_bedrooms": 0}
        
        # Build summary
        if tool_response and tool_response.get("summary"):
            summary = tool_response["summary"]
        else:
            summary = f"Found {len(properties)} properties with location analysis and Halloween decorations."
        
        return {
            "search_criteria": search_criteria,
            "properties": properties,
            "location_analyses": location_analyses,
            "decorated_images": decorated_images,
            "generated_at": datetime.now().isoformat(),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"[REPORT] Error building from filesystem: {str(e)}")
        return None


def serialize_interrupt(interrupt_data: list) -> list[dict[str, Any]]:
    """Convert interrupt objects to JSON-serializable format."""
    result = []
    for item in interrupt_data:
        if hasattr(item, "value"):
            result.append({"value": item.value})
        elif isinstance(item, dict):
            result.append(item)
    return result


@app.post("/api/invoke")
async def invoke_agent(
    request: AgentRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
) -> dict[str, Any]:
    """Start agent conversation. Returns interrupt if property review needed."""
    user_id = creds.decoded["sub"]
    thread_id = f"{user_id}-{request.timestamp}"
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"[INVOKE] Starting agent for thread {thread_id}")

    try:
        result = supervisor_agent.invoke(
            {"messages": request.messages},
            config
        )

        # Check for human-in-the-loop interrupt
        if "__interrupt__" in result:
            logger.info(f"[INVOKE] Interrupt triggered for property review")
            return {"__interrupt__": serialize_interrupt(result["__interrupt__"])}

        # Check for final report
        report = extract_final_report(result, thread_id)
        if report:
            logger.info(f"[INVOKE] Final report generated")
            return {"structured_response": report}

        # Return current state (agent still processing)
        return {
            "todos": result.get("todos", []),
            "message": "Agent processing"
        }

    except Exception as e:
        logger.error(f"[INVOKE] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume")
async def resume_agent(
    request: ResumeRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
) -> dict[str, Any]:
    """Resume agent after human review. Filters properties to approved ones."""
    user_id = creds.decoded["sub"]
    validate_thread_ownership(request.thread_id, user_id)
    config = {"configurable": {"thread_id": request.thread_id}}

    logger.info(f"[RESUME] Resuming thread {request.thread_id}")

    try:
        # Get current state to find pending interrupt
        state_snapshot = supervisor_agent.get_state(config)
        
        if not state_snapshot or not state_snapshot.tasks:
            raise HTTPException(status_code=400, detail="No pending interrupt found")

        # Extract interrupt ID, original action request, and properties
        interrupt_id = None
        original_action = None
        original_properties = []
        
        for task in state_snapshot.tasks:
            if hasattr(task, "interrupts") and task.interrupts:
                for interrupt in task.interrupts:
                    if hasattr(interrupt, "value"):
                        action_requests = interrupt.value.get("action_requests", [])
                        for action in action_requests:
                            if action.get("name") == "present_properties_for_review_tool":
                                interrupt_id = interrupt.id
                                original_action = action.copy()
                                original_properties = action.get("arguments", {}).get("properties", [])
                                break

        if not interrupt_id or not original_action:
            raise HTTPException(status_code=400, detail="No property review interrupt found")

        # Filter to only approved properties
        approved_ids = set(request.approved_properties or [])
        filtered_properties = [
            p for p in original_properties
            if (p.get("id") if isinstance(p, dict) else getattr(p, "id", None)) in approved_ids
        ]

        logger.info(f"[RESUME] Approved {len(filtered_properties)} of {len(original_properties)} properties")

        # Build resume command with correct HITL format
        # Use interrupt ID as key, with edited_action containing modified arguments
        if len(filtered_properties) == len(original_properties):
            # All properties approved - use simple approve
            resume_payload = {
                interrupt_id: {"decisions": [{"type": "approve"}]}
            }
        else:
            # Some properties filtered - use edit with modified action
            edited_action = original_action.copy()
            edited_action["arguments"] = {"properties": filtered_properties}
            resume_payload = {
                interrupt_id: {
                    "decisions": [{
                        "type": "edit",
                        "edited_action": edited_action
                    }]
                }
            }

        resume_command = Command(resume=resume_payload)
        result = supervisor_agent.invoke(resume_command, config)

        # Check for another interrupt
        if "__interrupt__" in result:
            logger.info(f"[RESUME] Another interrupt triggered")
            return {"__interrupt__": serialize_interrupt(result["__interrupt__"])}

        # Check for final report
        report = extract_final_report(result, request.thread_id)
        if report:
            logger.info(f"[RESUME] Final report generated")
            return {"structured_response": report}

        # Return current state
        return {
            "todos": result.get("todos", []),
            "message": "Agent processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RESUME] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/state")
async def get_agent_state(
    request: StateRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
) -> dict[str, Any]:
    """Get current agent state for a thread."""
    user_id = creds.decoded["sub"]
    validate_thread_ownership(request.thread_id, user_id)
    config = {"configurable": {"thread_id": request.thread_id}}

    logger.info(f"[STATE] Getting state for thread {request.thread_id}")

    try:
        state_snapshot = supervisor_agent.get_state(config)
        
        if not state_snapshot or not state_snapshot.values:
            raise HTTPException(status_code=404, detail="Thread not found")

        values = state_snapshot.values

        # Check for final report
        report = extract_final_report(values, request.thread_id)

        return {
            "structured_response": report,
            "todos": values.get("todos", []),
            "approved_properties": values.get("approved_properties", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[STATE] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/decorated-image/{property_id}")
async def get_decorated_image(
    property_id: str,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
) -> dict[str, Any]:
    """Fetch Halloween-decorated image for a property."""
    file_path = Path("decorated_images") / f"{property_id}_halloween.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Decorated image not found")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid image data")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

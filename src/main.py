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


def parse_json_content(content: Any) -> dict | None:
    """Parse JSON content from string or dict."""
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
    return None


def extract_json_from_text(text: str) -> dict | None:
    """Extract JSON object from text that may contain markdown code blocks."""
    import re
    # Try to find JSON in code blocks first
    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    # Try to find raw JSON object
    json_match = re.search(r'\{[^{}]*"(?:status|properties|property_id)"[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def extract_data_from_messages(messages: list) -> tuple[list, dict, dict]:
    """Extract property and location data from agent messages."""
    properties = []
    location_analyses = {}
    decorated_images = {}
    
    for msg in messages:
        content = getattr(msg, "content", "") if hasattr(msg, "content") else str(msg)
        if not isinstance(content, str):
            continue
        
        # Look for property search results
        if '"properties"' in content and '"status"' in content:
            data = extract_json_from_text(content)
            if data and "properties" in data:
                for prop in data["properties"]:
                    if isinstance(prop, dict) and prop.get("id"):
                        properties.append(prop)
                        logger.info(f"[REPORT] Extracted property from message: {prop.get('id')}")
        
        # Look for location analysis results
        if '"property_id"' in content and '"nearby_pois"' in content:
            data = extract_json_from_text(content)
            if data and "property_id" in data:
                prop_id = data["property_id"]
                location_analyses[prop_id] = data
                logger.info(f"[REPORT] Extracted location from message: {prop_id}")
    
    # Read decorated images from external disk (these are always saved there)
    decorated_dir = Path("decorated_images")
    if decorated_dir.exists():
        for file_path in decorated_dir.glob("*_halloween.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                prop_id = data.get("property_id", file_path.stem.replace("_halloween", ""))
                decorated_images[prop_id] = str(file_path)
                logger.info(f"[REPORT] Found decorated image: {prop_id}")
            except Exception as e:
                logger.warning(f"[REPORT] Failed to read {file_path}: {e}")
    
    return properties, location_analyses, decorated_images


def build_report_from_filesystem(thread_id: str, tool_response: dict | None) -> dict | None:
    """Build PropertyReport from disk and agent messages."""
    from src.agent import AGENT_DATA_DIR, supervisor_agent
    from datetime import datetime
    
    try:
        logger.info(f"[REPORT] Reading from disk: {AGENT_DATA_DIR}")
        
        properties = []
        location_analyses = {}
        decorated_images = {}
        
        # First try reading from real disk
        properties_dir = Path(AGENT_DATA_DIR) / "properties"
        if properties_dir.exists():
            for file_path in properties_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    properties.append(data)
                    logger.info(f"[REPORT] Found property on disk: {data.get('id', file_path.stem)}")
                except Exception as e:
                    logger.warning(f"[REPORT] Failed to read {file_path}: {e}")
        
        locations_dir = Path(AGENT_DATA_DIR) / "locations"
        if locations_dir.exists():
            for file_path in locations_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    prop_id = data.get("property_id") or data.get("id") or file_path.stem.replace("_location", "")
                    location_analyses[prop_id] = data
                    logger.info(f"[REPORT] Found location on disk: {prop_id}")
                except Exception as e:
                    logger.warning(f"[REPORT] Failed to read {file_path}: {e}")
        
        decorations_dir = Path(AGENT_DATA_DIR) / "decorations"
        if decorations_dir.exists():
            for file_path in decorations_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    prop_id = data.get("property_id") or data.get("id") or file_path.stem
                    external_path = data.get("external_disk_path", "")
                    decorated_images[prop_id] = external_path
                    logger.info(f"[REPORT] Found decoration on disk: {prop_id}")
                except Exception as e:
                    logger.warning(f"[REPORT] Failed to read {file_path}: {e}")
        
        # If disk is empty, extract from agent messages
        if not properties:
            logger.info("[REPORT] Disk empty, extracting from agent messages")
            config = {"configurable": {"thread_id": thread_id}}
            state = supervisor_agent.get_state(config)
            if state and state.values:
                messages = state.values.get("messages", [])
                msg_props, msg_locs, msg_decs = extract_data_from_messages(messages)
                properties = msg_props
                if not location_analyses:
                    location_analyses = msg_locs
                if not decorated_images:
                    decorated_images = msg_decs
        
        # Build search criteria
        search_criteria = tool_response.get("search_criteria", {}) if tool_response else {}
        if not search_criteria:
            search_criteria = {"location": "Unknown", "max_price": 0, "min_bedrooms": 0}
        
        # Build summary
        summary = tool_response.get("summary", "") if tool_response else ""
        if not summary:
            summary = f"Found {len(properties)} properties with location analysis and Halloween decorations."
        
        logger.info(f"[REPORT] Built report: {len(properties)} properties, {len(location_analyses)} locations, {len(decorated_images)} decorations")
        
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
        import traceback
        logger.error(traceback.format_exc())
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
                                # Check both "arguments" and "args" keys
                                args_data = action.get("arguments") or action.get("args") or {}
                                original_properties = args_data.get("properties", [])
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

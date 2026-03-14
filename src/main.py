"""
FastAPI server for AI Real Estate Co-Pilot.

Handles agent invocation, human-in-the-loop interrupts, and final report delivery.
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from dotenv import load_dotenv

import src.agent as agent_module
from src.models import AgentRequest, ResumeRequest, StateRequest
from src.tools import reset_browser_use_counter

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle for FastAPI."""
    logger.info("[STARTUP] Initializing supervisor agent...")
    logger.info("[STARTUP] Supervisor agent ready")
    yield
    logger.info("[SHUTDOWN] Done")


app = FastAPI(title="AI Real Estate Co-Pilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


AGENT_DATA_DIR = Path("agent_data")
DECORATED_IMAGES_DIR = Path("decorated_images")

def clear_previous_agent_data():
    """Delete previously saved properties, locations, and decorations from disk."""
    directories_to_clear = [
        AGENT_DATA_DIR / "properties",
        AGENT_DATA_DIR / "locations",
        AGENT_DATA_DIR / "decorations",
        DECORATED_IMAGES_DIR
    ]
    
    deleted_count = 0
    for directory in directories_to_clear:
        if directory.exists():
            for file_path in directory.glob("*.json"):
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"[CLEANUP] Failed to delete {file_path}: {e}")
                    
    logger.info(f"[CLEANUP] Deleted {deleted_count} stale JSON output files.")

def extract_final_report(state: dict, thread_id: str) -> dict | None:
    """Read final_report.json from disk (written by the agent via write_file).
    
    The FilesystemBackend saves agent files to ./agent_data/ on real disk.
    The supervisor writes the full JSON report to /final_report.json.
    We read it here, parse it, and pass the structured data to the frontend.
    """
    report_path = AGENT_DATA_DIR / "final_report.json"
    
    if report_path.exists():
        try:
            import re as _re
            json_text = report_path.read_text(encoding="utf-8").strip()
            
            if json_text:
                # Strip markdown code fences if present
                if json_text.startswith("```"):
                    match = _re.search(r'```(?:json)?\s*(.+?)\s*```', json_text, _re.DOTALL)
                    if match:
                        json_text = match.group(1).strip()

                # Attempt 1: direct parse
                report_data = None
                try:
                    report_data = json.loads(json_text)
                except json.JSONDecodeError:
                    pass

                # Attempt 2: truncate at last valid closing brace (handles "Extra data" errors)
                if report_data is None:
                    try:
                        last_brace = json_text.rfind('}')
                        if last_brace != -1:
                            report_data = json.loads(json_text[:last_brace + 1])
                    except json.JSONDecodeError:
                        pass

                # Attempt 3: regex-extract the outermost JSON object
                if report_data is None:
                    match = _re.search(r'(\{.*\})', json_text, _re.DOTALL)
                    if match:
                        try:
                            report_data = json.loads(match.group(1))
                        except json.JSONDecodeError:
                            pass

                if report_data:
                    logger.info(f"[REPORT] Read final_report.json with {len(report_data.get('properties', []))} properties")
                    # Inject property `id` from disk files if the agent omitted it
                    props_on_disk = {}
                    props_dir = AGENT_DATA_DIR / "properties"
                    if props_dir.exists():
                        for pf in sorted(props_dir.glob("*.json")):
                            try:
                                pd = json.loads(pf.read_text(encoding="utf-8"))
                                if pd.get("id"):
                                    props_on_disk[pd["id"]] = pd
                            except Exception:
                                pass
                    disk_ids = list(props_on_disk.keys())
                    for i, prop in enumerate(report_data.get("properties", [])):
                        if not prop.get("id") and i < len(disk_ids):
                            prop["id"] = disk_ids[i]
                            logger.info(f"[REPORT] Injected id={disk_ids[i]} into property[{i}]")
                    report_path.unlink(missing_ok=True)
                    return report_data
                else:
                    logger.error("[REPORT] All JSON parse attempts failed — file may be completely malformed")
        except Exception as e:
            logger.error(f"[REPORT] Error reading final_report.json: {e}")
    
    logger.info("[REPORT] final_report.json not found on disk yet")
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
        for file_path in decorated_dir.glob("*_decorated.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                prop_id = data.get("property_id", file_path.stem.replace("_decorated", ""))
                decorated_images[prop_id] = str(file_path)
                logger.info(f"[REPORT] Found decorated image: {prop_id}")
            except Exception as e:
                logger.warning(f"[REPORT] Failed to read {file_path}: {e}")
    
    return properties, location_analyses, decorated_images


def build_report_from_filesystem(thread_id: str, tool_response: dict | None) -> dict | None:
    """Build PropertyReport from disk and agent messages."""
    from src.tools import AGENT_DATA_DIR
    from src.agent import supervisor
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
            state = agent_module.supervisor.get_state(config)
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
            summary = f"Found {len(properties)} properties with location analysis and interior decorations."
        
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
async def invoke_agent(request: AgentRequest) -> dict[str, Any]:
    """Start agent conversation. Returns interrupt if property review needed."""
    thread_id = f"thread-{request.timestamp}"
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 2000
    }

    logger.info(f"[INVOKE] Starting agent for thread {thread_id}")
    clear_previous_agent_data()

    try:
        result = agent_module.supervisor.invoke(
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


@app.post("/api/stream")
async def stream_agent(request: AgentRequest):
    """Stream agent progress via SSE. Emits which agent is working and estimated progress."""
    thread_id = f"thread-{request.timestamp}"
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 2000
    }

    logger.info(f"[STREAM] Starting agent stream for thread {thread_id}")
    clear_previous_agent_data()

    # Reset the browser-use call counter for each new search
    reset_browser_use_counter()

    # Progress map: subagent_type -> (start%, end%)
    # Search phase: 0-50% (ends at interrupt for HITL review)
    PROGRESS_MAP = {
        "property_search": (5, 45),
    }

    def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'progress', 'agent': 'supervisor', 'progress': 0, 'thread_id': thread_id})}\n\n"

            current_subagent = None
            subagent_steps = 0

            # v2 streaming format per Deep Agents docs: yields dicts with type/ns/data keys
            for chunk in agent_module.supervisor.stream(
                {"messages": request.messages},
                config,
                stream_mode="updates",
                subgraphs=True,
                version="v2",
            ):
                if chunk.get("type") != "updates":
                    continue

                ns = chunk.get("ns", ())
                data = chunk.get("data", {})
                is_subagent = any(s.startswith("tools:") for s in ns)

                for node_name, node_data in data.items():
                    # Subagent started (main agent model_request with task tool calls)
                    if not ns and node_name == "model_request":
                        for msg in node_data.get("messages", []):
                            for tc in getattr(msg, "tool_calls", []):
                                if tc["name"] == "task":
                                    current_subagent = tc["args"].get("subagent_type", "unknown")
                                    subagent_steps = 0
                                    start_pct = PROGRESS_MAP.get(current_subagent, (10, 40))[0]
                                    yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent, 'progress': start_pct})}\n\n"

                    # Subagent running — increment progress within its range
                    elif is_subagent and current_subagent:
                        subagent_steps += 1
                        start_pct, end_pct = PROGRESS_MAP.get(current_subagent, (10, 40))
                        step_pct = min(start_pct + (subagent_steps * 3), end_pct - 5)
                        yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent, 'progress': step_pct})}\n\n"

                    # Subagent result returned to main agent
                    elif not ns and node_name == "tools":
                        for msg in node_data.get("messages", []):
                            if hasattr(msg, "type") and msg.type == "tool":
                                end_pct = PROGRESS_MAP.get(current_subagent, (10, 40))[1]
                                yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent or 'supervisor', 'progress': end_pct})}\n\n"
                                current_subagent = None

            # Check final state for interrupt or report
            state_snapshot = agent_module.supervisor.get_state(config)
            if state_snapshot and state_snapshot.values:
                if state_snapshot.tasks:
                    for task in state_snapshot.tasks:
                        if hasattr(task, "interrupts") and task.interrupts:
                            properties = []
                            for interrupt in task.interrupts:
                                if hasattr(interrupt, "value"):
                                    for action in interrupt.value.get("action_requests", []):
                                        if action.get("name") == "present_properties_for_review_tool":
                                            args = action.get("args") or action.get("arguments") or {}
                                            properties = args.get("properties", [])
                                            break
                            yield f"data: {json.dumps({'type': 'interrupt', 'progress': 50, 'properties': properties, 'data': serialize_interrupt(task.interrupts)})}\n\n"
                            yield "data: [DONE]\n\n"
                            return

                report = extract_final_report(state_snapshot.values, thread_id)
                if report:
                    yield f"data: {json.dumps({'type': 'report', 'progress': 100, 'data': report})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"[STREAM] Error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/stream-resume")
async def stream_resume(request: ResumeRequest):
    """Stream the post-review phase via SSE (location analysis, decoration, final report)."""
    config = {"configurable": {"thread_id": request.thread_id}}

    logger.info(f"[STREAM-RESUME] Resuming thread {request.thread_id}")

    # Build resume command
    state_snapshot = agent_module.supervisor.get_state(config)
    if not state_snapshot or not state_snapshot.tasks:
        raise HTTPException(status_code=400, detail="No pending interrupt found")

    original_action = None
    original_properties = []
    for task in state_snapshot.tasks:
        if hasattr(task, "interrupts") and task.interrupts:
            for interrupt in task.interrupts:
                if hasattr(interrupt, "value"):
                    for action in interrupt.value.get("action_requests", []):
                        if action.get("name") == "present_properties_for_review_tool":
                            original_action = action.copy()
                            args_data = action.get("args") or action.get("arguments") or {}
                            original_properties = args_data.get("properties", [])
                            break

    if not original_action:
        raise HTTPException(status_code=400, detail="No property review interrupt found")

    approved_ids = set(request.approved_properties or [])
    filtered_properties = [
        p for p in original_properties
        if (p.get("id") if isinstance(p, dict) else getattr(p, "id", None)) in approved_ids
    ]

    if len(filtered_properties) == len(original_properties):
        decisions = [{"type": "approve"}]
    else:
        decisions = [{
            "type": "edit",
            "edited_action": {
                "name": original_action["name"],
                "args": {"properties": filtered_properties}
            }
        }]

    resume_command = Command(resume={"decisions": decisions})

    # Post-review progress: location_analysis 55-75%, interior_decorator 75-90%, report 90-100%
    RESUME_PROGRESS = {
        "location_analysis": (55, 75),
        "interior_decorator": (75, 90),
    }

    def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'progress', 'agent': 'supervisor', 'progress': 50})}\n\n"

            current_subagent = None
            subagent_steps = 0

            # v2 streaming format per Deep Agents docs
            for chunk in agent_module.supervisor.stream(
                resume_command,
                config,
                stream_mode="updates",
                subgraphs=True,
                version="v2",
            ):
                if chunk.get("type") != "updates":
                    continue

                ns = chunk.get("ns", ())
                data = chunk.get("data", {})
                is_subagent = any(s.startswith("tools:") for s in ns)

                for node_name, node_data in data.items():
                    if not ns and node_name == "model_request":
                        for msg in node_data.get("messages", []):
                            for tc in getattr(msg, "tool_calls", []):
                                if tc["name"] == "task":
                                    current_subagent = tc["args"].get("subagent_type", "unknown")
                                    subagent_steps = 0
                                    start_pct = RESUME_PROGRESS.get(current_subagent, (55, 75))[0]
                                    yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent, 'progress': start_pct})}\n\n"

                    elif is_subagent and current_subagent:
                        subagent_steps += 1
                        start_pct, end_pct = RESUME_PROGRESS.get(current_subagent, (55, 75))
                        step_pct = min(start_pct + (subagent_steps * 2), end_pct - 5)
                        yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent, 'progress': step_pct})}\n\n"

                    elif not ns and node_name == "tools":
                        for msg in node_data.get("messages", []):
                            if hasattr(msg, "type") and msg.type == "tool":
                                end_pct = RESUME_PROGRESS.get(current_subagent, (55, 75))[1]
                                yield f"data: {json.dumps({'type': 'progress', 'agent': current_subagent or 'supervisor', 'progress': end_pct})}\n\n"
                                current_subagent = None

            # Final report — read from disk (agent writes /final_report.json)
            final_state = agent_module.supervisor.get_state(config)
            if final_state and final_state.values:
                report = extract_final_report(final_state.values, request.thread_id)
                if report:
                    yield f"data: {json.dumps({'type': 'report', 'progress': 100, 'data': report})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"[STREAM-RESUME] Error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/resume")
async def resume_agent(request: ResumeRequest) -> dict[str, Any]:
    """Resume agent after human review. Filters properties to approved ones."""
    config = {
        "configurable": {"thread_id": request.thread_id},
        "recursion_limit": 2000
    }

    logger.info(f"[RESUME] Resuming thread {request.thread_id}")

    try:
        # Get current state to find pending interrupt
        state_snapshot = agent_module.supervisor.get_state(config)
        
        if not state_snapshot or not state_snapshot.tasks:
            raise HTTPException(status_code=400, detail="No pending interrupt found")

        # Extract original action request and properties from interrupt
        original_action = None
        original_properties = []
        
        for task in state_snapshot.tasks:
            if hasattr(task, "interrupts") and task.interrupts:
                for interrupt in task.interrupts:
                    if hasattr(interrupt, "value"):
                        action_requests = interrupt.value.get("action_requests", [])
                        for action in action_requests:
                            if action.get("name") == "present_properties_for_review_tool":
                                original_action = action.copy()
                                args_data = action.get("args") or action.get("arguments") or {}
                                original_properties = args_data.get("properties", [])
                                break

        if not original_action:
            raise HTTPException(status_code=400, detail="No property review interrupt found")

        # Filter to only approved properties
        approved_ids = set(request.approved_properties or [])
        filtered_properties = [
            p for p in original_properties
            if (p.get("id") if isinstance(p, dict) else getattr(p, "id", None)) in approved_ids
        ]

        logger.info(f"[RESUME] Approved {len(filtered_properties)} of {len(original_properties)} properties")

        # Build resume command per Deep Agents HITL docs:
        # Command(resume={"decisions": [{"type": "approve"|"edit"|"reject", ...}]})
        if len(filtered_properties) == len(original_properties):
            decisions = [{"type": "approve"}]
        else:
            decisions = [{
                "type": "edit",
                "edited_action": {
                    "name": original_action["name"],
                    "args": {"properties": filtered_properties}
                }
            }]

        resume_command = Command(resume={"decisions": decisions})
        result = agent_module.supervisor.invoke(resume_command, config)

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
async def get_agent_state(request: StateRequest) -> dict[str, Any]:
    """Get current agent state for a thread."""
    config = {"configurable": {"thread_id": request.thread_id}}

    logger.info(f"[STATE] Getting state for thread {request.thread_id}")

    try:
        state_snapshot = agent_module.supervisor.get_state(config)
        
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


@app.get("/api/interior-image/{property_id}")
async def get_decorated_image(property_id: str) -> dict[str, Any]:
    """Fetch interior-decorated image for a property."""
    file_path = Path("decorated_images") / f"{property_id}_decorated.json"
    
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

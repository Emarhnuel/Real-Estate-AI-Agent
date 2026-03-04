"""
Output guardrails for AI Real Estate Co-Pilot sub-agents.
"""

import json
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime


REQUIRED_PROPERTY_FIELDS = {"id", "address", "price", "bedrooms", "bathrooms",
                             "property_type", "listing_url", "image_urls", "description"}


class PropertyOutputGuardrail(AgentMiddleware):
    """Validates that the property search agent used real tools and produced complete data."""

    @hook_config(can_jump_to=["model"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        if not messages:
            return None

        # Check 1: Verify browser_task was actually called
        tool_names_used = {
            msg.name for msg in messages
            if hasattr(msg, "name") and msg.type == "tool"
        }
        used_browser = "browser_task" in tool_names_used

        # Check 2: Validate property JSON files written via write_file
        files = state.get("files", {})
        property_files = {k: v for k, v in files.items() if k.startswith("/properties/")}

        issues = []

        if not used_browser:
            issues.append("You did NOT use browser_task. You MUST use browser_task to scrape real listing pages.")

        if not property_files:
            issues.append("No property files found in /properties/. You MUST save each property as JSON.")
        else:
            for path, file_data in property_files.items():
                content = file_data.get("content", [])
                text = "\n".join(content) if isinstance(content, list) else str(content)
                try:
                    prop = json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    issues.append(f"{path}: Invalid JSON.")
                    continue

                missing = REQUIRED_PROPERTY_FIELDS - set(prop.keys())
                if missing:
                    issues.append(f"{path}: Missing fields: {', '.join(sorted(missing))}")

                url = prop.get("listing_url", "")
                if not isinstance(url, str) or not url.startswith("http"):
                    issues.append(f"{path}: listing_url must be a real URL, got '{url}'")

        if issues:
            # Jump back to model so agent can fix the issues
            return {
                "messages": [{
                    "role": "user",
                    "content": (
                        "OUTPUT VALIDATION FAILED. Fix these issues before finishing:\n"
                        + "\n".join(f"- {i}" for i in issues)
                    )
                }],
                "jump_to": "model"
            }

        return None

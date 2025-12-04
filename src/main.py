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

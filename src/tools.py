"""
Tools for AI Real Estate Co-Pilot.

This module provides external API integrations including Tavily search
for property listings.
"""

import os
from typing import Dict, Any
from tavily import TavilyClient


def tavily_search_tool(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced",
    include_images: bool = True
) -> Dict[str, Any]:
    """
    Search for property listings using Tavily API.
    
    Args:
        query: Search query for property listings
        max_results: Maximum number of results to return
        search_depth: Search depth - "basic" or "advanced"
        include_images: Include image URLs from results
        
    Returns:
        Dictionary with search results including images
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_images=include_images
        )
        return response
    except Exception as e:
        raise Exception(f"Tavily search failed: {str(e)}")

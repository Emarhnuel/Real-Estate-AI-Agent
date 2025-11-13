"""
Pydantic models for AI Real Estate Co-Pilot.

This module defines all data models used throughout the application including
property data, search criteria, location analysis, and API request/response models.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Property(BaseModel):
    """Property listing model with all relevant details."""
    
    id: str = Field(..., description="Unique identifier for the property")
    address: str = Field(..., description="Street address of the property")
    city: str = Field(..., description="City where property is located")
    state: str = Field(..., description="State where property is located")
    zip_code: str = Field(..., description="ZIP code of the property")
    price: float = Field(..., description="Listing price in USD")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: float = Field(..., description="Number of bathrooms")
    square_feet: int = Field(..., description="Total square footage")
    property_type: str = Field(..., description="Type: house, condo, apartment, etc.")
    listing_url: str = Field(..., description="URL to the original listing")
    image_urls: list[str] = Field(default_factory=list, description="List of image URLs")
    description: str = Field(..., description="Property description text")
    listing_date: datetime = Field(..., description="Date property was listed")


class SearchCriteria(BaseModel):
    """User's property search criteria."""
    
    location: str = Field(..., description="City, neighborhood, or zip code")
    min_price: Optional[float] = Field(None, description="Minimum price in USD")
    max_price: Optional[float] = Field(None, description="Maximum price in USD")
    min_bedrooms: Optional[int] = Field(None, description="Minimum number of bedrooms")
    max_bedrooms: Optional[int] = Field(None, description="Maximum number of bedrooms")
    min_bathrooms: Optional[float] = Field(None, description="Minimum number of bathrooms")
    property_types: list[str] = Field(
        default_factory=list,
        description="List of property types: house, condo, apartment, etc."
    )
    max_results: int = Field(default=10, description="Maximum number of results to return")


class PointOfInterest(BaseModel):
    """A nearby point of interest for location analysis."""
    
    name: str = Field(..., description="Name of the point of interest")
    category: str = Field(
        ...,
        description="Category: shopping, school, transit, park, workplace"
    )
    distance_meters: float = Field(..., description="Distance from property in meters")
    address: str = Field(..., description="Address of the point of interest")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class LocationAnalysis(BaseModel):
    """Location analysis for a property including nearby amenities."""
    
    property_id: str = Field(..., description="ID of the property being analyzed")
    latitude: float = Field(..., description="Property latitude")
    longitude: float = Field(..., description="Property longitude")
    nearby_pois: list[PointOfInterest] = Field(
        default_factory=list,
        description="List of nearby points of interest"
    )
    pros: list[str] = Field(
        default_factory=list,
        description="Location advantages based on analysis"
    )
    cons: list[str] = Field(
        default_factory=list,
        description="Location disadvantages based on analysis"
    )
    walkability_score: Optional[int] = Field(
        None,
        description="Walkability score 0-100 if available"
    )
    transit_score: Optional[int] = Field(
        None,
        description="Transit score 0-100 if available"
    )


class PropertyReport(BaseModel):
    """Final comprehensive property report."""
    
    search_criteria: SearchCriteria = Field(..., description="Original search criteria")
    properties: list[Property] = Field(
        default_factory=list,
        description="List of properties in the report"
    )
    location_analyses: dict[str, LocationAnalysis] = Field(
        default_factory=dict,
        description="Location analysis mapped by property_id"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when report was generated"
    )
    summary: str = Field(..., description="Executive summary of findings")


class AgentRequest(BaseModel):
    """Request model for agent invocation."""
    
    messages: list[dict] = Field(..., description="List of conversation messages")
    timestamp: int = Field(..., description="Unix timestamp for thread ID generation")


class ResumeRequest(BaseModel):
    """Request model for resuming agent after interrupt."""
    
    thread_id: str = Field(..., description="Thread ID to resume")
    approved_properties: Optional[list[str]] = Field(
        None,
        description="List of approved property IDs"
    )

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
    address: str = Field(default="Unknown", description="Street address of the property")
    city: str = Field(default="Unknown", description="City where property is located")
    state: str = Field(default="Unknown", description="State where property is located")
    zip_code: str = Field(default="Unknown", description="ZIP code of the property")
    price: Optional[float] = Field(None, description="Listing price in USD")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, description="Total square footage")
    property_type: str = Field(default="Unknown", description="Type: house, condo, apartment, etc.")
    listing_url: str = Field(default="", description="URL to the original listing")
    image_urls: list[str] = Field(default_factory=list, description="List of image URLs")
    description: str = Field(default="", description="Property description text")
    listing_date: Optional[str] = Field(None, description="Date property was listed (string format)")


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
    
    property_id: str = Field(default="", description="ID of the property being analyzed")
    latitude: float = Field(default=0.0, description="Property latitude")
    longitude: float = Field(default=0.0, description="Property longitude")
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

class PropertyForReview(BaseModel):
    """Property data for user review."""
    
    id: str = Field(..., description="Property identifier")
    address: str = Field(..., description="Full property address")
    price: float = Field(..., description="Listing price")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: float = Field(..., description="Number of bathrooms")
    listing_url: str = Field(..., description="URL to the property listing")
    image_urls: list[str] = Field(..., description="Property image URLs")


class DecoratedImage(BaseModel):
    """Halloween-decorated property image."""
    
    property_id: str = Field(..., description="ID of the property this image belongs to")
    original_image_url: str = Field(..., description="URL of the original property image")
    decorated_image_base64: str = Field(..., description="Base64-encoded decorated image")
    decorations_added: str = Field(default="", description="Description of decorations added")


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
    decorated_images: dict[str, DecoratedImage] = Field(
        default_factory=dict,
        description="Halloween-decorated images mapped by property_id"
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


# CHANGE: Added a specific Pydantic model for the /api/state endpoint request.
class StateRequest(BaseModel):
    """Request model for getting agent state."""
    
    thread_id: str = Field(..., description="Thread ID to get state for")
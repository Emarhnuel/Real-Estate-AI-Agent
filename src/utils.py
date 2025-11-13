"""
Utility functions for AI Real Estate Co-Pilot.

This module provides helper functions for reading property and location data
from the filesystem and compiling comprehensive property reports.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from src.models import Property, LocationAnalysis, PropertyReport, SearchCriteria


def read_property_files(properties_dir: str = "/properties/") -> List[Property]:
    """
    Read all property JSON files from the filesystem.
    
    Args:
        properties_dir: Directory path where property files are stored
        
    Returns:
        List of Property objects parsed from JSON files
    """
    properties = []
    
    # In Deep Agents, filesystem paths are virtual
    # This function will be called by the agent with read_file tool
    # For now, return empty list as placeholder
    # The actual implementation will use the agent's read_file tool
    
    return properties


def read_location_files(locations_dir: str = "/locations/") -> Dict[str, LocationAnalysis]:
    """
    Read all location analysis JSON files from the filesystem.
    
    Args:
        locations_dir: Directory path where location analysis files are stored
        
    Returns:
        Dictionary mapping property_id to LocationAnalysis objects
    """
    location_analyses = {}
    
    # In Deep Agents, filesystem paths are virtual
    # This function will be called by the agent with read_file tool
    # For now, return empty dict as placeholder
    # The actual implementation will use the agent's read_file tool
    
    return location_analyses


def compile_property_report(
    search_criteria: SearchCriteria,
    properties: List[Property],
    location_analyses: Dict[str, LocationAnalysis]
) -> PropertyReport:
    """
    Compile a comprehensive property report from properties and location analyses.
    
    Args:
        search_criteria: Original search criteria from user
        properties: List of approved properties
        location_analyses: Dictionary of location analyses by property_id
        
    Returns:
        PropertyReport with all compiled data
    """
    # Generate summary
    summary_parts = []
    summary_parts.append(f"Found {len(properties)} properties matching your criteria in {search_criteria.location}.")
    
    if search_criteria.max_price:
        summary_parts.append(f"Price range: ${search_criteria.min_price or 0:,.0f} - ${search_criteria.max_price:,.0f}.")
    
    if search_criteria.min_bedrooms:
        summary_parts.append(f"Bedrooms: {search_criteria.min_bedrooms}+.")
    
    # Add location highlights
    if location_analyses:
        summary_parts.append(f"Detailed location analysis included for all {len(location_analyses)} properties.")
    
    summary = " ".join(summary_parts)
    
    # Create report
    report = PropertyReport(
        search_criteria=search_criteria,
        properties=properties,
        location_analyses=location_analyses,
        generated_at=datetime.now(),
        summary=summary
    )
    
    return report


def format_property_report_text(report: PropertyReport) -> str:
    """
    Format a PropertyReport into human-readable text.
    
    Args:
        report: PropertyReport to format
        
    Returns:
        Formatted text representation of the report
    """
    lines = []
    lines.append("=" * 80)
    lines.append("PROPERTY SEARCH REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(report.summary)
    lines.append("")
    
    # Search Criteria
    lines.append("SEARCH CRITERIA")
    lines.append("-" * 80)
    lines.append(f"Location: {report.search_criteria.location}")
    if report.search_criteria.max_price:
        lines.append(f"Price Range: ${report.search_criteria.min_price or 0:,.0f} - ${report.search_criteria.max_price:,.0f}")
    if report.search_criteria.min_bedrooms:
        lines.append(f"Bedrooms: {report.search_criteria.min_bedrooms}+")
    if report.search_criteria.min_bathrooms:
        lines.append(f"Bathrooms: {report.search_criteria.min_bathrooms}+")
    if report.search_criteria.property_types:
        lines.append(f"Property Types: {', '.join(report.search_criteria.property_types)}")
    lines.append("")
    
    # Properties
    lines.append("PROPERTIES")
    lines.append("=" * 80)
    
    for idx, prop in enumerate(report.properties, 1):
        lines.append("")
        lines.append(f"PROPERTY #{idx}: {prop.address}")
        lines.append("-" * 80)
        lines.append(f"Price: ${prop.price:,.0f}")
        lines.append(f"Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
        lines.append(f"Square Feet: {prop.square_feet:,}")
        lines.append(f"Type: {prop.property_type}")
        lines.append(f"Listing URL: {prop.listing_url}")
        
        if prop.image_urls:
            lines.append(f"Images: {len(prop.image_urls)} available")
            lines.append(f"  - {prop.image_urls[0]}")
        
        lines.append("")
        lines.append("Description:")
        lines.append(prop.description[:300] + "..." if len(prop.description) > 300 else prop.description)
        
        # Location Analysis
        if prop.id in report.location_analyses:
            analysis = report.location_analyses[prop.id]
            lines.append("")
            lines.append("LOCATION ANALYSIS")
            lines.append("-" * 40)
            
            # Pros
            if analysis.pros:
                lines.append("Pros:")
                for pro in analysis.pros:
                    lines.append(f"  ✓ {pro}")
            
            # Cons
            if analysis.cons:
                lines.append("Cons:")
                for con in analysis.cons:
                    lines.append(f"  ✗ {con}")
            
            # Nearby POIs summary
            if analysis.nearby_pois:
                lines.append("")
                lines.append(f"Nearby Points of Interest: {len(analysis.nearby_pois)} found")
                
                # Group by category
                categories = {}
                for poi in analysis.nearby_pois:
                    if poi.category not in categories:
                        categories[poi.category] = []
                    categories[poi.category].append(poi)
                
                for category, pois in categories.items():
                    lines.append(f"  {category.title()}: {len(pois)} locations")
                    # Show closest 2
                    for poi in sorted(pois, key=lambda p: p.distance_meters)[:2]:
                        distance_km = poi.distance_meters / 1000
                        lines.append(f"    - {poi.name} ({distance_km:.1f}km)")
            
            # Scores
            if analysis.walkability_score:
                lines.append(f"Walkability Score: {analysis.walkability_score}/100")
            if analysis.transit_score:
                lines.append(f"Transit Score: {analysis.transit_score}/100")
        
        lines.append("")
    
    lines.append("=" * 80)
    lines.append(f"Report generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def parse_property_from_json(json_str: str) -> Property:
    """
    Parse a Property object from JSON string.
    
    Args:
        json_str: JSON string containing property data
        
    Returns:
        Property object
    """
    data = json.loads(json_str)
    return Property(**data)


def parse_location_analysis_from_json(json_str: str) -> LocationAnalysis:
    """
    Parse a LocationAnalysis object from JSON string.
    
    Args:
        json_str: JSON string containing location analysis data
        
    Returns:
        LocationAnalysis object
    """
    data = json.loads(json_str)
    return LocationAnalysis(**data)

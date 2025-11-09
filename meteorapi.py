"""
FastAPI application for testing Meteomatics Meteor Shower API endpoints.

Based on: https://www.meteomatics.com/en/api/available-parameters/meteor-showers/

Available meteor showers:
- geminids
- perseids
- quadrantids
- eta_aquariids
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import httpx
from enum import Enum

app = FastAPI(
    title="Meteor Shower API",
    description="Test endpoints for Meteomatics Meteor Shower Visibility API",
    version="1.0.0"
)


class MeteorShower(str, Enum):
    """Available meteor showers"""
    GEMINIDS = "geminids"
    PERSEIDS = "perseids"
    QUADRANTIDS = "quadrantids"
    ETA_AQUARIIDS = "eta_aquariids"


class MeteorShowerRequest(BaseModel):
    """Request model for meteor shower visibility"""
    shower: MeteorShower = Field(..., description="Name of the meteor shower")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of location")
    datetime: str = Field(
        ..., 
        description="ISO datetime in format YYYY-MM-DDTHH:MM:SSZ",
        example="2025-01-03T01:00:00Z"
    )
    username: Optional[str] = Field(None, description="Meteomatics API username")
    password: Optional[str] = Field(None, description="Meteomatics API password")


class MeteorShowerResponse(BaseModel):
    """Response model for meteor shower visibility"""
    shower: str
    location: dict
    datetime: str
    visibility_index: Optional[float] = None
    api_url: str
    status: str
    message: Optional[str] = None


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Meteor Shower API - Testing Meteomatics endpoints",
        "documentation": "/docs",
        "available_showers": [shower.value for shower in MeteorShower],
        "endpoints": {
            "get_visibility": "/meteor-shower/visibility",
            "test_endpoint": "/meteor-shower/test",
            "build_url": "/meteor-shower/build-url"
        }
    }


@app.get("/meteor-showers", tags=["Info"])
async def list_meteor_showers():
    """List all available meteor showers with their peak dates"""
    return {
        "meteor_showers": [
            {
                "name": "Quadrantids",
                "id": "quadrantids",
                "peak": "January 3-4",
                "active_period": "December 28 - January 12",
                "zhr": "~120 meteors/hour"
            },
            {
                "name": "Eta Aquariids",
                "id": "eta_aquariids",
                "peak": "May 5-6",
                "active_period": "April 19 - May 28",
                "zhr": "~50 meteors/hour"
            },
            {
                "name": "Perseids",
                "id": "perseids",
                "peak": "August 12-13",
                "active_period": "July 17 - August 24",
                "zhr": "~100 meteors/hour"
            },
            {
                "name": "Geminids",
                "id": "geminids",
                "peak": "December 13-14",
                "active_period": "December 4 - December 17",
                "zhr": "~120 meteors/hour"
            }
        ]
    }


@app.post("/meteor-shower/visibility", 
          response_model=MeteorShowerResponse,
          tags=["Meteor Shower"])
async def get_meteor_shower_visibility(request: MeteorShowerRequest):
    """
    Get meteor shower visibility for a specific location and time.
    
    This endpoint calls the Meteomatics API to get the visibility index.
    You need valid Meteomatics API credentials to get real data.
    
    **Parameters:**
    - **shower**: Name of the meteor shower (geminids, perseids, quadrantids, eta_aquariids)
    - **latitude**: Latitude of the observation location (-90 to 90)
    - **longitude**: Longitude of the observation location (-180 to 180)
    - **datetime**: ISO datetime string (e.g., "2025-01-03T01:00:00Z")
    - **username**: Meteomatics API username (optional for testing)
    - **password**: Meteomatics API password (optional for testing)
    
    **Returns:**
    - Visibility index (0-100, higher = better visibility)
    - Location and time information
    - API URL used for the request
    """
    
    # Build the Meteomatics API URL
    # Format: https://api.meteomatics.com/{datetime}/{parameter}/{location}/json
    parameter = f"meteor_showers_{request.shower.value}_visibility:idx"
    location = f"{request.latitude},{request.longitude}"
    
    api_url = f"https://api.meteomatics.com/{request.datetime}/{parameter}/{location}/json"
    
    response_data = {
        "shower": request.shower.value,
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        "datetime": request.datetime,
        "api_url": api_url,
        "status": "success"
    }
    
    # If credentials provided, make actual API call
    if request.username and request.password:
        try:
            async with httpx.AsyncClient() as client:
                api_response = await client.get(
                    api_url,
                    auth=(request.username, request.password),
                    timeout=30.0
                )
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    # Extract visibility index from response
                    if "data" in data and len(data["data"]) > 0:
                        if "coordinates" in data["data"][0] and len(data["data"][0]["coordinates"]) > 0:
                            if "dates" in data["data"][0]["coordinates"][0] and len(data["data"][0]["coordinates"][0]["dates"]) > 0:
                                response_data["visibility_index"] = data["data"][0]["coordinates"][0]["dates"][0]["value"]
                elif api_response.status_code == 401:
                    response_data["status"] = "error"
                    response_data["message"] = "Invalid credentials"
                else:
                    response_data["status"] = "error"
                    response_data["message"] = f"API error: {api_response.status_code}"
                    
        except Exception as e:
            response_data["status"] = "error"
            response_data["message"] = f"Request failed: {str(e)}"
    else:
        response_data["message"] = "Mock response - provide credentials for real data"
        response_data["visibility_index"] = 75.5  # Mock value
    
    return response_data


@app.get("/meteor-shower/test", tags=["Testing"])
async def test_meteor_shower_endpoint(
    shower: MeteorShower = Query(..., description="Meteor shower name"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    date: str = Query(
        "2025-01-03T01:00:00Z",
        description="Datetime in ISO format",
        example="2025-01-03T01:00:00Z"
    )
):
    """
    Simple GET endpoint to test meteor shower visibility.
    
    **Example:**
    `/meteor-shower/test?shower=quadrantids&lat=40.7128&lon=-74.0060&date=2025-01-03T01:00:00Z`
    """
    
    parameter = f"meteor_showers_{shower.value}_visibility:idx"
    location = f"{lat},{lon}"
    api_url = f"https://api.meteomatics.com/{date}/{parameter}/{location}/json"
    
    return {
        "shower": shower.value,
        "location": {"latitude": lat, "longitude": lon},
        "datetime": date,
        "api_url": api_url,
        "note": "This is a test endpoint. Use POST /meteor-shower/visibility with credentials for real data.",
        "mock_visibility_index": 82.3
    }


@app.get("/meteor-shower/build-url", tags=["Utilities"])
async def build_meteomatics_url(
    shower: MeteorShower = Query(..., description="Meteor shower name"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    date: str = Query(..., description="Datetime in ISO format"),
    format: Literal["json", "html", "csv", "xml"] = Query("json", description="Response format")
):
    """
    Build a Meteomatics API URL for meteor shower visibility.
    
    **Supported formats:**
    - json: JSON response
    - html: HTML visualization
    - csv: CSV data
    - xml: XML response
    """
    
    parameter = f"meteor_showers_{shower.value}_visibility:idx"
    location = f"{lat},{lon}"
    
    api_url = f"https://api.meteomatics.com/{date}/{parameter}/{location}/{format}"
    
    return {
        "shower": shower.value,
        "location": {"latitude": lat, "longitude": lon},
        "datetime": date,
        "format": format,
        "api_url": api_url,
        "usage": "Copy this URL and add your credentials: https://USERNAME:PASSWORD@api.meteomatics.com/..."
    }


@app.get("/meteor-shower/area-visibility", tags=["Meteor Shower"])
async def get_area_visibility(
    shower: MeteorShower = Query(..., description="Meteor shower name"),
    lat_min: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    lon_min: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    lat_max: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    lon_max: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    date: str = Query(..., description="Datetime in ISO format"),
    resolution: float = Query(0.1, description="Grid resolution in degrees")
):
    """
    Build API URL for meteor shower visibility over an area (grid).
    
    **Example:**
    Get visibility for quadrantids over Europe:
    - lat_min=36, lon_min=-10, lat_max=56, lon_max=20
    - resolution=0.1
    """
    
    parameter = f"meteor_showers_{shower.value}_visibility:idx"
    grid = f"{lat_max},{lon_min}_{lat_min},{lon_max}:{resolution},{resolution}"
    
    api_url = f"https://api.meteomatics.com/{date}/{parameter}/{grid}/json"
    html_map_url = f"https://api.meteomatics.com/{date}/{parameter}/{grid}/html_map"
    
    return {
        "shower": shower.value,
        "area": {
            "lat_min": lat_min,
            "lon_min": lon_min,
            "lat_max": lat_max,
            "lon_max": lon_max
        },
        "datetime": date,
        "resolution": resolution,
        "api_url": api_url,
        "html_map_url": html_map_url,
        "note": "Add credentials to URL for actual data"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Meteor Shower API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

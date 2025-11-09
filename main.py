from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import httpx
from pydantic import BaseModel, Field
import json

app = FastAPI(
    title="Overpass API Roadway Testing Suite",
    description="Comprehensive API for testing all roadway data endpoints using Overpass API",
    version="1.0.0"
)

# Overpass API base URL
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Response model
class OverpassResponse(BaseModel):
    query: str
    data: dict
    element_count: int

# Helper function to validate and parse bbox
def validate_bbox(bbox: str) -> str:
    """Validate and format bounding box coordinates"""
    try:
        coords = [float(x.strip()) for x in bbox.split(',')]
        if len(coords) != 4:
            raise ValueError("Bbox must have exactly 4 coordinates")
        south, west, north, east = coords
        if not (-90 <= south <= 90 and -90 <= north <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= west <= 180 and -180 <= east <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if south >= north:
            raise ValueError("South must be less than North")
        return f"{south},{west},{north},{east}"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid bbox format: {str(e)}")

# Helper function to execute Overpass queries
async def execute_overpass_query(query: str) -> dict:
    """Execute an Overpass API query and return the results"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                OVERPASS_URL,
                data={"data": query},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            result = response.json()
            return result
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            raise HTTPException(status_code=500, detail=f"Overpass API error: {error_detail}")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Overpass API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Overpass API Roadway Testing Suite",
        "docs": "/docs",
        "total_endpoints": 30,
        "description": "Test comprehensive roadway data from OpenStreetMap"
    }

# ============= ENDPOINT 1: Basic Road Network =============
@app.get("/api/roads/basic-network", tags=["Basic Road Info"])
async def get_basic_road_network(
    bbox: str = Query(..., description="Bounding box: south,west,north,east", example="51.5,-0.1,51.6,0.0"),
    highway_type: Optional[str] = Query(None, description="Filter by highway type (motorway, primary, residential, etc.)")
):
    """
    Get basic road network with geometries and coordinates.
    
    **Returns:**
    - Road geometries
    - Coordinates
    - Basic way information
    - OSM IDs
    """
    validated_bbox = validate_bbox(bbox)
    highway_filter = f'["highway"="{highway_type}"]' if highway_type else '["highway"]'
    query = f"""[out:json][timeout:25];(way{highway_filter}({validated_bbox}););out geom;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 2: Road Classification & Types =============
@app.get("/api/roads/classification", tags=["Basic Road Info"])
async def get_road_classification(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    types: str = Query("motorway|trunk|primary|secondary|tertiary|residential|service", 
                       description="Pipe-separated highway types")
):
    """
    Get roads by classification/hierarchy.
    
    **Returns:**
    - Highway type (motorway, trunk, primary, secondary, tertiary, residential, service)
    - Road hierarchy
    - Classification metadata
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25];(way["highway"~"{types}"]({validated_bbox}););out body;>;out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 3: Surface Quality & Material =============
@app.get("/api/roads/surface", tags=["Road Condition"])
async def get_road_surface(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    surface_type: Optional[str] = Query(None, description="Filter by surface (asphalt, concrete, gravel, dirt, paved, unpaved)")
):
    """
    Get road surface material and quality information.
    
    **Returns:**
    - surface (asphalt, concrete, gravel, dirt, paved, unpaved)
    - smoothness (excellent, good, intermediate, bad, very_bad)
    - tracktype
    - Surface condition
    """
    surface_filter = f'["surface"="{surface_type}"]' if surface_type else '["surface"]'
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]{surface_filter}({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 4: Lane Information =============
@app.get("/api/roads/lanes", tags=["Road Geometry"])
async def get_lane_information(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    min_lanes: Optional[int] = Query(None, description="Minimum number of lanes")
):
    """
    Get detailed lane information for roads.
    
    **Returns:**
    - lanes (total number)
    - lanes:forward
    - lanes:backward
    - turn:lanes
    - turn:lanes:forward
    - turn:lanes:backward
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["lanes"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 5: Speed Limits =============
@app.get("/api/roads/speed-limits", tags=["Traffic Regulation"])
async def get_speed_limits(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    maxspeed: Optional[str] = Query(None, description="Filter by specific speed limit (e.g., '50', '30')")
):
    """
    Get speed limit information for roads.
    
    **Returns:**
    - maxspeed (general speed limit)
    - maxspeed:forward
    - maxspeed:backward
    - maxspeed:conditional
    - source:maxspeed
    """
    speed_filter = f'["maxspeed"="{maxspeed}"]' if maxspeed else '["maxspeed"]'
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]{speed_filter}({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 6: One-Way Streets =============
@app.get("/api/roads/oneway", tags=["Traffic Regulation"])
async def get_oneway_streets(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get one-way street information.
    
    **Returns:**
    - oneway (yes, no, -1 for reverse direction)
    - Direction of travel
    - Reversible lanes info
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["oneway"="yes"]({validated_bbox}); way["highway"]["oneway"="-1"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 7: Road Width =============
@app.get("/api/roads/width", tags=["Road Geometry"])
async def get_road_width(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get road width information.
    
    **Returns:**
    - width (in meters)
    - width:lanes
    - est_width (estimated width)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["width"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 8: Traffic Signals =============
@app.get("/api/roads/traffic-signals", tags=["Traffic Control"])
async def get_traffic_signals(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get traffic signal locations and details.
    
    **Returns:**
    - Traffic light coordinates
    - traffic_signals:direction
    - button_operated
    - crossing
    - Signal timing info
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["highway"="traffic_signals"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 9: Stop Signs & Yield =============
@app.get("/api/roads/stop-yield", tags=["Traffic Control"])
async def get_stop_yield_signs(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get stop signs and yield/give way signs.
    
    **Returns:**
    - Stop sign locations
    - Give way (yield) sign locations
    - Direction information
    - Associated road info
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["highway"="stop"]({validated_bbox}); node["highway"="give_way"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 10: Crosswalks & Pedestrian Crossings =============
@app.get("/api/roads/crosswalks", tags=["Pedestrian Infrastructure"])
async def get_crosswalks(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get crosswalk and pedestrian crossing information.
    
    **Returns:**
    - crossing (uncontrolled, traffic_signals, zebra, unmarked)
    - tactile_paving (yes/no)
    - supervised (yes/no)
    - crossing_ref
    - Crossing geometry
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["highway"="crossing"]({validated_bbox}); way["footway"="crossing"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 11: Street Lighting =============
@app.get("/api/roads/lighting", tags=["Road Features"])
async def get_street_lighting(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    lit: Optional[str] = Query(None, description="Filter by lighting status (yes, no, automatic, 24/7)")
):
    """
    Get street lighting information.
    
    **Returns:**
    - lit (yes, no, automatic, 24/7, disused)
    - lit:by_gaslight
    - Lighting coverage
    """
    lit_filter = f'["lit"="{lit}"]' if lit else '["lit"]'
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]{lit_filter}({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 12: Road Access Restrictions =============
@app.get("/api/roads/access-restrictions", tags=["Traffic Regulation"])
async def get_access_restrictions(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get road access restriction information.
    
    **Returns:**
    - access (private, permissive, destination, no, yes)
    - motor_vehicle access
    - hgv (heavy goods vehicle) access
    - psv (public service vehicle) access
    - bicycle access
    - foot access
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["access"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 13: Bridges & Tunnels =============
@app.get("/api/roads/bridges-tunnels", tags=["Road Features"])
async def get_bridges_tunnels(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    feature_type: Optional[str] = Query(None, description="Filter by type: bridge or tunnel")
):
    """
    Get bridge and tunnel information.
    
    **Returns:**
    - bridge (yes, viaduct, aqueduct)
    - tunnel (yes, building_passage)
    - layer (vertical ordering)
    - level
    - Structure name
    """
    if feature_type == "bridge":
        type_filter = '["bridge"="yes"]'
    elif feature_type == "tunnel":
        type_filter = '["tunnel"="yes"]'
    else:
        type_filter = '["bridge"]' if feature_type is None else '["bridge"]["tunnel"]'
    
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["bridge"="yes"]({validated_bbox}); way["highway"]["tunnel"="yes"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 14: Turn Restrictions =============
@app.get("/api/roads/turn-restrictions", tags=["Traffic Regulation"])
async def get_turn_restrictions(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get turn restriction information.
    
    **Returns:**
    - restriction (no_left_turn, no_right_turn, no_u_turn, no_straight_on, only_right_turn, etc.)
    - except (vehicle exceptions)
    - from/to/via members
    - Conditional restrictions
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( relation["type"="restriction"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 15: Parking Information =============
@app.get("/api/roads/parking", tags=["Parking"])
async def get_parking_info(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get parking lane and parking area information.
    
    **Returns:**
    - parking:lane:both/left/right (parallel, perpendicular, diagonal, no_parking, no_stopping)
    - parking:condition
    - amenity=parking
    - capacity
    - fee
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["parking:lane"]({validated_bbox}); way["amenity"="parking"]({validated_bbox}); node["amenity"="parking"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 16: Sidewalks =============
@app.get("/api/roads/sidewalks", tags=["Pedestrian Infrastructure"])
async def get_sidewalks(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get sidewalk information along roads.
    
    **Returns:**
    - sidewalk (both, left, right, no, separate)
    - sidewalk:both/left/right (yes, no)
    - sidewalk:surface
    - sidewalk:width
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["sidewalk"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 17: Bicycle Infrastructure =============
@app.get("/api/roads/bicycle-infrastructure", tags=["Bicycle Infrastructure"])
async def get_bicycle_infrastructure(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get bicycle lane and path information.
    
    **Returns:**
    - cycleway (lane, track, shared_lane, opposite, opposite_lane)
    - cycleway:left/right
    - cycleway:surface
    - highway=cycleway
    - bicycle=yes/designated
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["cycleway"]({validated_bbox}); way["highway"="cycleway"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 18: Road Names & References =============
@app.get("/api/roads/names-references", tags=["Basic Road Info"])
async def get_road_names(
    bbox: str = Query(..., description="Bounding box: south,west,north,east"),
    has_ref: bool = Query(False, description="Filter roads with route references")
):
    """
    Get road names and reference numbers.
    
    **Returns:**
    - name (street name)
    - ref (route number/reference)
    - int_ref (international reference)
    - nat_ref (national reference)
    - reg_ref (regional reference)
    - alt_name (alternative name)
    """
    ref_filter = '["ref"]' if has_ref else ''
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["name"]{ref_filter}({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 19: Road Condition & Maintenance =============
@app.get("/api/roads/condition", tags=["Road Condition"])
async def get_road_condition(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get road condition and maintenance information.
    
    **Returns:**
    - condition
    - check_date
    - fixme (issues to fix)
    - FIXME
    - note (maintenance notes)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["condition"]({validated_bbox}); way["highway"]["fixme"]({validated_bbox}); way["highway"]["check_date"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 20: Toll Roads =============
@app.get("/api/roads/toll", tags=["Traffic Regulation"])
async def get_toll_roads(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get toll road information.
    
    **Returns:**
    - toll (yes, no)
    - toll:hgv (heavy goods vehicles)
    - charge (toll amount)
    - toll:method (electronic, cash)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["toll"="yes"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 21: Motorway Junctions & Exits =============
@app.get("/api/roads/motorway-junctions", tags=["Road Features"])
async def get_motorway_junctions(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get motorway junction and exit information.
    
    **Returns:**
    - ref (exit number)
    - name (junction name)
    - exit_to (destination)
    - junction (motorway_junction, roundabout)
    - Coordinates
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["highway"="motorway_junction"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 22: Road Elevation & Incline =============
@app.get("/api/roads/elevation", tags=["Road Geometry"])
async def get_road_elevation(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get road elevation and incline information.
    
    **Returns:**
    - incline (up, down, percentage value)
    - ele (elevation in meters)
    - Gradient information
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["incline"]({validated_bbox}); way["highway"]["ele"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 23: Bus Stops & Public Transport =============
@app.get("/api/roads/bus-stops", tags=["Public Transport"])
async def get_bus_stops(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get bus stop information.
    
    **Returns:**
    - name (stop name)
    - ref (stop reference)
    - network (transport network)
    - operator
    - shelter (yes/no)
    - bench (yes/no)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["highway"="bus_stop"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 24: Railway Crossings =============
@app.get("/api/roads/railway-crossings", tags=["Traffic Control"])
async def get_railway_crossings(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get railway level crossing information.
    
    **Returns:**
    - Crossing type
    - crossing:barrier (yes, no)
    - crossing:light (yes, no)
    - crossing:bell (yes, no)
    - supervised (yes, no)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["railway"="level_crossing"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 25: Emergency Access =============
@app.get("/api/roads/emergency-access", tags=["Traffic Regulation"])
async def get_emergency_access(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get emergency vehicle access information.
    
    **Returns:**
    - emergency (yes, designated, no, private)
    - Emergency vehicle routing
    - Fire hydrant locations
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["emergency"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 26: Road Construction Status =============
@app.get("/api/roads/construction", tags=["Road Condition"])
async def get_construction_roads(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get roads under construction or proposed.
    
    **Returns:**
    - highway=construction
    - construction (road type being built)
    - opening_date
    - proposed
    - Construction status
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"="construction"]({validated_bbox}); way["highway"="proposed"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 27: Turn Lanes Detail =============
@app.get("/api/roads/turn-lanes", tags=["Road Geometry"])
async def get_turn_lanes(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get detailed turn lane information.
    
    **Returns:**
    - turn:lanes (lane-by-lane turn permissions)
    - turn:lanes:forward
    - turn:lanes:backward
    - Values: left, through, right, slight_left, slight_right, sharp_left, sharp_right, merge_to_left, merge_to_right
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["turn:lanes"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 28: Vehicle Restrictions =============
@app.get("/api/roads/vehicle-restrictions", tags=["Traffic Regulation"])
async def get_vehicle_restrictions(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get vehicle size and weight restrictions.
    
    **Returns:**
    - maxweight (maximum weight in tonnes)
    - maxheight (maximum height in meters)
    - maxlength (maximum length in meters)
    - maxwidth (maximum width in meters)
    - maxaxleload
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["maxweight"]({validated_bbox}); way["highway"]["maxheight"]({validated_bbox}); way["highway"]["maxlength"]({validated_bbox}); way["highway"]["maxwidth"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 29: Service Roads =============
@app.get("/api/roads/service-roads", tags=["Basic Road Info"])
async def get_service_roads(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get service road and delivery access information.
    
    **Returns:**
    - service (alley, driveway, parking_aisle, drive-through, emergency_access)
    - Service road classification
    - Access information
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"="service"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= ENDPOINT 30: Road Shoulders =============
@app.get("/api/roads/shoulders", tags=["Road Geometry"])
async def get_road_shoulders(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get road shoulder information.
    
    **Returns:**
    - shoulder (yes, no, both, left, right)
    - shoulder:width
    - shoulder:surface
    - Shoulder availability
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["shoulder"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

# ============= BONUS ENDPOINTS =============

@app.get("/api/roads/roundabouts", tags=["Road Features"])
async def get_roundabouts(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get roundabout information.
    
    **Returns:**
    - junction=roundabout
    - Roundabout geometry
    - Direction (clockwise/counterclockwise)
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["junction"="roundabout"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

@app.get("/api/roads/speed-bumps", tags=["Traffic Control"])
async def get_speed_bumps(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get speed bump and traffic calming information.
    
    **Returns:**
    - traffic_calming (bump, hump, table, chicane, cushion)
    - Location coordinates
    - Surface type
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( node["traffic_calming"]({validated_bbox}); ); out body;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

@app.get("/api/roads/street-names-multilingual", tags=["Basic Road Info"])
async def get_multilingual_names(
    bbox: str = Query(..., description="Bounding box: south,west,north,east")
):
    """
    Get multilingual road names.
    
    **Returns:**
    - name (default name)
    - name:en (English name)
    - name:fr (French name)
    - name:es (Spanish name)
    - int_name (international name)
    - All language variants
    """
    validated_bbox = validate_bbox(bbox)
    query = f"""[out:json][timeout:25]; ( way["highway"]["name"]({validated_bbox}); ); out body; >; out skel qt;"""
    data = await execute_overpass_query(query)
    return {
        "query": query,
        "data": data,
        "element_count": len(data.get("elements", []))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

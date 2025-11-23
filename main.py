import time
import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from minio import Minio
import uvicorn
import geopandas as gpd
import rasterio
import trimesh
import pandas as pd
from fastkml import kml # <-- NEW LINE

# --- 1. CONFIGURATION ---
MINIO_ENDPOINT = "127.0.0.1:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "site-analysis-poc" 

# Initialize MinIO client
try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False 
    )
    found = minio_client.bucket_exists(BUCKET_NAME)
    if not found:
        minio_client.make_bucket(BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")
    else:
        print(f"Bucket '{BUCKET_NAME}' already exists.")
except Exception as e:
    print(f"Error connecting to MinIO: {e}")
    exit()

app = FastAPI()

@app.post("/api/v1/uploads/custom-data")
async def upload_custom_data(
    file: UploadFile = File(...)
):
    
    # --- 2. SAVE FILE TEMPORARILY ---
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())

    # --- 3. METRIC 1: TIME TO UPLOAD TO MINIO ---
    print(f"Starting MinIO upload for {file.filename}...")
    gcs_start_time = time.time()
    
    blob_name = f"uploads/{uuid.uuid4()}-{file.filename}"
    
    minio_client.fput_object(
        BUCKET_NAME, blob_name, temp_filename
    )
    
    gcs_end_time = time.time()
    gcs_elapsed = gcs_end_time - gcs_start_time
    print(f"METRIC: Time to upload {file.filename} to MinIO: {gcs_elapsed:.4f} seconds")

    # --- 4. METRIC 2: TIME TO PARSE FILE ---
    print(f"Starting file parse for {file.filename}...")
    parse_start_time = time.time()
    
    try:
        # --- THIS IS THE UPDATED LOGIC BLOCK ---
        if file.filename.endswith('.tif') or file.filename.endswith('.tiff'):
            with rasterio.open(temp_filename) as dataset:
                print(f"Parsed GeoTIFF: {dataset.count} bands, {dataset.width}x{dataset.height}")
        
        elif file.filename.endswith('.obj'):
            mesh = trimesh.load_mesh(temp_filename)
            print(f"Parsed OBJ File: {len(mesh.vertices)} vertices, {len(mesh.faces)}")

        elif file.filename.endswith('.kml'): # <-- UPDATED BLOCK
            # Use fastkml to parse KML
            k = kml.KML()
            # Read the file from disk (fastkml needs the file path)
            with open(temp_filename, 'rb') as f:
                k.from_string(f.read())
            # We can't easily count features, so just print a success message
            print(f"Parsed KML File successfully.")
        
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(temp_filename)
            lon_col = next((col for col in df.columns if col.lower() in ['lon', 'long', 'longitude', 'x']), None)
            lat_col = next((col for col in df.columns if col.lower() in ['lat', 'latitude', 'y']), None)

            if lon_col and lat_col:
                gdf = gpd.GeoDataFrame(
                    df, 
                    geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
                    crs="EPSG:4326"
                )
                print(f"Parsed CSV File: {len(gdf)} features (points)")
            else:
                print(f"Parsed CSV File: {len(df)} rows (no geometry)")

        else:
            # For SHP, GeoJSON, etc., use the fast 'pyogrio' engine
            gdf = gpd.read_file(temp_filename, engine="pyogrio")
            print(f"Parsed Vector File: {len(gdf)} features")
            
    except Exception as e:
        print(f"ERROR parsing file: {e}")
        os.remove(temp_filename)
        raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")
    
    parse_end_time = time.time()
    parse_elapsed = parse_end_time - parse_start_time
    print(f"METRIC: Time to parse {file.filename}: {parse_elapsed:.4f} seconds")

    # --- 5. CLEANUP & RESPONSE ---
    os.remove(temp_filename) # Delete the temp file

    return {
      "fileName": file.filename,
      "minio_upload_time_seconds": gcs_elapsed,
      "file_parse_time_seconds": parse_elapsed,
      "minio_url": f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{blob_name}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
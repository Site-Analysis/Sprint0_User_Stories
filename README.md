# GIS Upload & Parse PoC (FastAPI + MinIO)

This Proof of Concept benchmarks server-side performance for uploading and parsing large GIS files. It uses:

- Backend: FastAPI + Uvicorn
- Storage: MinIO (S3-compatible)
- Parsing: GeoPandas (via Pyogrio) for vectors, Rasterio for rasters
- Frontend: a single static `index.html` with a simple upload form

The backend prints performance metrics to the terminal:
- Time to upload (to MinIO)
- Time to parse (GeoPandas/Rasterio)

## 1) Prerequisites

- MinIO server running locally (default in `main.py` is `127.0.0.1:9000` with `minioadmin/minioadmin`).
  - You can change `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, and `BUCKET_NAME` at the top of `main.py`.
- Conda (Miniconda or Anaconda) on Windows.

## 2) Create the environment (conda-forge)

Use conda-forge for reliable GIS builds on Windows.

```powershell
# Create and activate environment
conda create -n site-analysis-poc -c conda-forge python=3.11 -y
conda activate site-analysis-poc

# Install runtime deps
conda install -c conda-forge fastapi uvicorn geopandas pyogrio rasterio minio python-multipart -y
```

Notes:
- `python-multipart` is required for `UploadFile` handling in FastAPI (multipart/form-data parsing).
- `geopandas`, `pyogrio`, and `rasterio` will pull in GDAL/PROJ and other native libs via conda-forge.

## 3) Project files

- `main.py` — FastAPI backend. Uploads the file to MinIO, then parses it and prints metrics.
- `index.html` — Simple uploader page; posts selected file to the backend endpoint.
- `mockup.png` — Visual guide for the form layout.

## 4) How to run

Open two terminals (or tabs) in the project folder `c:\Site analysis`.

- Terminal 1: Start the backend

```powershell
# From c:\Site analysis
conda activate site-analysis-poc
python .\main.py
```

- Browser: Open the uploader page

Double-click `index.html` (or open it in your browser). Use the form to pick a GIS file and submit.

The page sends a `POST` to:
```
http://127.0.0.1:8000/api/v1/uploads/custom-data
```
with `multipart/form-data` containing the file under the key `file`.

## 5) Where to see metrics

- The authoritative timing metrics ("Time to upload" and "Time to parse") are printed in the backend terminal (Terminal 1) by `main.py`.
- The browser (`index.html`) will display the JSON response with the measured values for convenience, but treat the backend logs as the source of truth.

## 6) Troubleshooting

- MinIO connection errors at startup
  - Ensure MinIO is running and reachable at `127.0.0.1:9000`.
  - If you changed credentials or endpoint, update the constants at the top of `main.py`.
- Large file parsing
  - Vector files: uses `GeoPandas` with `engine="pyogrio"`.
  - Raster files: opened with `rasterio`.
- CORS
  - If your browser blocks requests from a `file://` origin, add CORS middleware in `main.py` (optional for local PoC).

## 7) Sprint1 User Stories Summary

Project note carried over from remote branch:

> Sprint1_User_Stories – Tests Done for Sprint1 User Stories

This README consolidates both the PoC documentation and the prior sprint testing note.

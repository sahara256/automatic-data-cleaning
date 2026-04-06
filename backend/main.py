from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from io import BytesIO
import pandas as pd

from backend.cleaner import auto_data_cleaner

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- APP ----------------
app = FastAPI(
    title="Auto Data Cleaning API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- TEMP DIR ----------------
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)


# ---------------- HEALTH ----------------
@app.get("/test")
def health_check():
    return {"message": "API is running successfully 🚀", "status": "healthy"}


# ---------------- MAIN API ----------------
@app.post("/clean-data")
@app.post("/clean-data/")
async def clean_data(file: UploadFile = File(...)):
    input_path = None
    output_path = None

    try:
        # ✅ Validate file
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # ✅ Safe filename
        input_path = TEMP_DIR / "temp_input.csv"

        # ✅ FIXED FILE READ (IMPORTANT)
        contents = await file.read()

        with open(input_path, "wb") as f:
            f.write(contents)

        logger.info(f"File saved: {input_path}")

        # ---------------- CLEANING ----------------
        output_path, score = auto_data_cleaner(str(input_path))
        logger.info(f"Cleaning done. Score: {score}")

        # ✅ Ensure file exists
        if not Path(output_path).exists():
            raise HTTPException(status_code=500, detail="Output file not created")

        # ---------------- RESPONSE ----------------
        with open(output_path, "rb") as f:
            file_bytes = f.read()

        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=cleaned_data.xlsx",
                "X-Quality-Score": str(score)
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data cleaning failed: {str(e)}")

    finally:
        # ---------------- CLEANUP ----------------
        try:
            if input_path and Path(input_path).exists():
                os.remove(input_path)
                logger.info(f"Deleted: {input_path}")

            if output_path and Path(output_path).exists():
                os.remove(output_path)
                logger.info(f"Deleted: {output_path}")

        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "Auto Data Cleaning API", "docs": "/docs"}
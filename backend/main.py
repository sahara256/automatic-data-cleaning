from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging
from pathlib import Path

from cleaner import auto_data_cleaner

# ✅ Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auto Data Cleaning API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create temp directory
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

@app.get("/test")
def health_check():
    """Health check endpoint"""
    return {"message": "API is running successfully 🚀", "status": "healthy"}

@app.post("/clean-data")
@app.post("/clean-data/")
async def clean_data(file: UploadFile = File(...)):
    """
    Clean uploaded CSV file and return cleaned Excel file
    
    Args:
        file: CSV file to clean
        
    Returns:
        Excel file with cleaned data and quality score header
    """
    input_path = None
    output_path = None
    
    try:
        # ✅ Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # ✅ Save uploaded file
        input_path = TEMP_DIR / f"temp_{file.filename}"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {input_path}")
        
        # ✅ Clean data
        output_path, score = auto_data_cleaner(str(input_path))
        logger.info(f"Data cleaned. Quality score: {score}")
        
        # ✅ Read cleaned file
        with open(output_path, "rb") as f:
            file_bytes = f.read()
        
        logger.info(f"Response prepared: {len(file_bytes)} bytes")
        
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
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data cleaning failed: {str(e)}")
    
    finally:
        # ✅ Cleanup temporary files
        try:
            if input_path and input_path.exists():
                input_path.unlink()
                logger.info(f"Cleaned up: {input_path}")
            if output_path and Path(output_path).exists():
                Path(output_path).unlink()
                logger.info(f"Cleaned up: {output_path}")
        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Auto Data Cleaning API", "docs": "/docs"}

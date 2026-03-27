from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from cleaner import auto_data_cleaner

app = FastAPI()

# ✅ ADD THIS ROOT ROUTE (IMPORTANT)
@app.get("/")
def home():
    return {"message": "API is running successfully 🚀"}


# ✅ CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ MAIN API
@app.post("/clean-data/")
async def clean_data(file: UploadFile = File(...)):
    try:
        input_path = f"temp_{file.filename}"

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_path, score = auto_data_cleaner(input_path)

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
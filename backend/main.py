# from fastapi import FastAPI, UploadFile, File
# import shutil
# import os

# from cleaner import auto_data_cleaner

# app = FastAPI()

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @app.get("/")
# def home():
#     return {"message": "Backend running successfully 🚀"}


# @app.post("/clean-data/")
# async def clean_data(file: UploadFile = File(...)):

#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     # Save uploaded file
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Run cleaning
#     output_file, score = auto_data_cleaner(file_path)

#     return {
#         "file": output_file,
#         "quality_score": score
#     }

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import shutil
import os

from cleaner import auto_data_cleaner

app = FastAPI()


@app.post("/clean-data/")
async def clean_data(file: UploadFile = File(...)):

    try:
        print("📥 Received:", file.filename)

        input_path = f"temp_{file.filename}"

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("📁 Saved:", input_path)

        output_path, score = auto_data_cleaner(input_path)

        print("✅ Cleaned:", output_path)

        if not os.path.exists(output_path):
            raise ValueError("Output file not created")

        with open(output_path, "rb") as f:
            file_bytes = f.read()

        print("📦 Sending file size:", len(file_bytes))

        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=cleaned_data.xlsx",
                "X-Quality-Score": str(score)
            }
        )

    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
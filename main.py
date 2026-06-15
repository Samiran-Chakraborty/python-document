from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse


app = FastAPI()

@app.post("/api/v1/deliverables/generate")
def generate():
    
    # ✅ Simulate file generation
    file_path = "sample.pdf"

    return {
        "status": "SUCCESS",
        "message": "Document generated successfully",
        "file_url": "http://127.0.0.1:8000/api/v1/deliverables/download"
    }

@app.get("/api/v1/deliverables/download")
def download():
    return FileResponse(
        path="sample.pdf",
        filename="deliverable.pdf",
        media_type="application/pdf"
    )

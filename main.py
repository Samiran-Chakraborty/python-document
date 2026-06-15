from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

app = FastAPI()

class GenerateRequest(BaseModel):
    project_id: int
    project_plan_line_id: int
    template_id: str

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Document generation API is running"
    }

@app.post("/api/v1/deliverables/generate")
def generate_deliverable(req: GenerateRequest):
    
    file_path = "sample.pdf"  # your generated file path

    return FileResponse(
        path=file_path,
        filename="deliverable.pdf",
        media_type="application/pdf"
    )

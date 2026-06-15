from fastapi import FastAPI
from pydantic import BaseModel

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
    return {
        "status": "SUCCESS",
        "message": "API is working",
        "project_id": req.project_id,
        "project_plan_line_id": req.project_plan_line_id,
        "template_id": req.template_id
    }

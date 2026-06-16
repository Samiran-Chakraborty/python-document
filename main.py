from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from reportlab.pdfgen import canvas

app = FastAPI()


# This class accepts JSON request from APEX
class GenerateRequest(BaseModel):
    project_id: int
    project_plan_line_id: int
    template_id: str


@app.post("/api/v1/deliverables/generate")
def generate(req: GenerateRequest):

    # Create unique file name using project_plan_line_id + template_id
    file_name = f"output_{req.project_plan_line_id}_{req.template_id}.pdf"
    file_path = os.path.join(os.getcwd(), file_name)

    # Create PDF dynamically
    c = canvas.Canvas(file_path)
    c.drawString(100, 750, "Dynamic Document")
    c.drawString(100, 720, f"Project ID: {req.project_id}")
    c.drawString(100, 690, f"Project Plan Line ID: {req.project_plan_line_id}")
    c.drawString(100, 660, f"Template ID: {req.template_id}")
    c.drawString(100, 630, "Generated at runtime")
    c.save()

    # Return response to APEX
    return {
        "status": "SUCCESS",
        "message": "Document generated successfully",
        "type": "PDF",
        "link": f"https://python-document-new-2.onrender.com/api/v1/deliverables/download/{file_name}"
    }


@app.get("/api/v1/deliverables/download/{file_name}")
def download(file_name: str):

    file_path = os.path.join(os.getcwd(), file_name)

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/pdf"
    )

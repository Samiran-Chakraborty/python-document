from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from pathlib import Path
import os

app = FastAPI()

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

# Base URL used to build the download link returned to APEX
BASE_URL = os.getenv(
    "BASE_URL",
    "https://python-document-new-2.onrender.com"
)

# Directory to store generated PDF files
FILES_DIR = Path(os.getcwd()) / "generated_files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# Request model
# ------------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    project_id: int
    project_plan_line_id: int
    template_id: str


# ------------------------------------------------------------------------------
# Generate PDF endpoint
# ------------------------------------------------------------------------------

@app.post("/api/v1/deliverables/generate")
def generate(req: GenerateRequest):
    """
    Generates a PDF file and returns a download link.
    """

    # Build a unique file name
    file_name = f"output_{req.project_plan_line_id}_{req.template_id}.pdf"
    file_path = FILES_DIR / file_name

    # Create PDF dynamically
    c = canvas.Canvas(str(file_path))
    c.setTitle("Dynamic Document")
    c.drawString(100, 750, "Dynamic Document")
    c.drawString(100, 720, f"Project ID: {req.project_id}")
    c.drawString(100, 690, f"Project Plan Line ID: {req.project_plan_line_id}")
    c.drawString(100, 660, f"Template ID: {req.template_id}")
    c.drawString(100, 630, "Generated at runtime")
    c.save()

    # Return JSON response for APEX
    return {
        "status": "SUCCESS",
        "message": "Document generated successfully",
        "type": "PDF",
        "file_name": file_name,
        "link": f"{BASE_URL}/api/v1/deliverables/download/{file_name}"
    }


# ------------------------------------------------------------------------------
# Download PDF endpoint
# ------------------------------------------------------------------------------

@app.get("/api/v1/deliverables/download/{file_name}")
def download(file_name: str):
    """
    Downloads the generated PDF as an attachment.
    """

    # Prevent path traversal by only taking the file name
    safe_file_name = Path(file_name).name
    file_path = FILES_DIR / safe_file_name

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Force browser download using Content-Disposition: attachment
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=safe_file_name,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_file_name}"',
            "Cache-Control": "no-store"
        }
    )

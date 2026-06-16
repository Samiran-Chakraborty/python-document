from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from pathlib import Path
import os
import base64
import binascii
import mimetypes

app = FastAPI()

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

BASE_URL = os.getenv(
    "BASE_URL",
    "https://python-document-new-2.onrender.com"
)

FILES_DIR = Path(os.getcwd()) / "generated_files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# Request model
# ------------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    project_id: int
    project_plan_line_id: int
    template_id: str
    template_content: str
    template_file_name: str | None = None


# ------------------------------------------------------------------------------
# Generate endpoint
# ------------------------------------------------------------------------------

@app.post("/api/v1/deliverables/generate")
def generate(req: GenerateRequest):
    """
    Receives base64 template content from APEX,
    saves original file,
    creates a PDF preview,
    returns downloadable/displayable links.
    """

    try:
        # Step 1: decode base64 content received from APEX
        decoded_bytes = base64.b64decode(req.template_content)

    except binascii.Error:
        return {
            "status": "ERROR",
            "message": "Invalid base64 template content received from APEX"
        }

    try:
        # Step 2: decide original file name
        original_file_name = req.template_file_name or f"template_{req.project_plan_line_id}_{req.template_id}.bin"
        original_file_name = Path(original_file_name).name  # safety
        original_file_path = FILES_DIR / original_file_name

        # Step 3: save original file from cloud content
        with open(original_file_path, "wb") as f:
            f.write(decoded_bytes)

        # Step 4: create preview PDF
        preview_file_name = f"preview_{req.project_plan_line_id}_{req.template_id}.pdf"
        preview_file_path = FILES_DIR / preview_file_name

        c = canvas.Canvas(str(preview_file_path))
        c.setTitle("Template Preview")

        y = 800
        c.drawString(50, y, "Template Preview / Download Summary")
        y -= 30
        c.drawString(50, y, f"Project ID: {req.project_id}")
        y -= 20
        c.drawString(50, y, f"Project Plan Line ID: {req.project_plan_line_id}")
        y -= 20
        c.drawString(50, y, f"Template ID: {req.template_id}")
        y -= 20
        c.drawString(50, y, f"Original File Name: {original_file_name}")
        y -= 30

        # Step 5: if decoded file is text, show preview lines
        # If binary (docx/xlsx/etc.), show summary only
        try:
            decoded_text = decoded_bytes.decode("utf-8", errors="strict")
            c.drawString(50, y, "Template Content Preview:")
            y -= 20

            lines = decoded_text.splitlines()
            for line in lines[:20]:
                c.drawString(50, y, line[:110])  # avoid very long lines
                y -= 18
                if y < 50:
                    c.showPage()
                    y = 800
        except UnicodeDecodeError:
            c.drawString(50, y, "Template file is binary (for example DOCX/XLSX/PDF).")
            y -= 20
            c.drawString(50, y, "Content cannot be directly displayed as plain text.")
            y -= 20
            c.drawString(50, y, "Use the original file download link to open the actual file.")

        c.save()

        return {
            "status": "SUCCESS",
            "message": "Template content received and files created successfully",
            "type": "PDF",
            "file_name": preview_file_name,
            "link": f"{BASE_URL}/api/v1/deliverables/download/{preview_file_name}",
            "original_file_name": original_file_name,
            "original_file_link": f"{BASE_URL}/api/v1/deliverables/download/{original_file_name}"
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }


# ------------------------------------------------------------------------------
# Download endpoint
# ------------------------------------------------------------------------------

@app.get("/api/v1/deliverables/download/{file_name}")
def download(file_name: str):
    safe_file_name = Path(file_name).name
    file_path = FILES_DIR / safe_file_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_file_name,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_file_name}"',
            "Cache-Control": "no-store"
        }
    )

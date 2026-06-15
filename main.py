from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from reportlab.pdfgen import canvas

app = FastAPI()


@app.post("/api/v1/deliverables/generate")
def generate():

    file_path = "output.pdf"

    # ✅ Create PDF dynamically
    c = canvas.Canvas(file_path)
    c.drawString(100, 750, "Dynamic Document")
    c.drawString(100, 720, "Generated at runtime ✅")
    c.drawString(100, 690, "Project Document Example")
    c.save()

    return {
        "status": "SUCCESS",
        "message": "Document generated",
        "file_url": "https://python-document-new-2.onrender.com/api/v1/deliverables/download"
    }


@app.get("/api/v1/deliverables/download")
def download():

    file_path = os.path.join(os.getcwd(), "output.pdf")

    return FileResponse(
        path=file_path,
        filename="deliverable.pdf",
        media_type="application/pdf"
    )

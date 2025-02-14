from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from routers import items, users
import os
import random
import PyPDF2
from docx import Document
from io import BytesIO
from PIL import Image
import numpy as np
from fastapi import Request
import easyocr

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="My FastAPI App",
    description="A clean and organized FastAPI application",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(upload_dir: str) -> str:
    while True:
        # Генерируем id для файла 
        filename = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        file_path = os.path.join(upload_dir, filename)
        if not os.path.exists(file_path):
            return filename

def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_file = BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    docx_file = BytesIO(file_content)
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(file_content: bytes) -> str:
    reader = easyocr.Reader(['ru', 'en'], gpu=False)
    image = Image.open(BytesIO(file_content))
    image_np = np.array(image)
    results = reader.readtext(image_np)
    text = '\n'.join([result[1] for result in results if result[1].strip()])
    return text

def extract_text_from_txt(file_content: bytes) -> str:
    return file_content.decode('utf-8')

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
        )

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_content = await file.read()
    
    try:
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        # Определяем тип отправленного файла 
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(file_content)
        elif file_extension == 'docx':
            extracted_text = extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            extracted_text = extract_text_from_txt(file_content)
        elif file_extension in {'png', 'jpg', 'jpeg'}:
            extracted_text = extract_text_from_image(file_content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )

    # Тут генерируем уникальное имя файла
    unique_filename = generate_unique_filename(upload_dir)
    file_location = os.path.join(upload_dir, unique_filename)
    
    with open(file_location, "w", encoding='utf-8') as file_object:
        file_object.write(extracted_text)
    
    return {
        "original_filename": file.filename,
        "saved_filename": unique_filename,
        "saved_location": file_location,
        "message": "File content extracted and saved successfully"
    }

class TextRequest(BaseModel):
    text: str

def process_text_content(text: str) -> tuple[str, bool]:
    try:
        punctuation_marks = set('.,!?;:()[]{}«»""\'\"—–-')
        if any(char in punctuation_marks for char in text):
            return text, False
            
        processed_text = text.replace(" ", "")
        return processed_text, True
    except Exception:
        return text, False

@app.post("/process-text/")
async def process_text(text_request: TextRequest):
    try:
        processed_text, success = process_text_content(text_request.text)
        message = "Text processed successfully" if success else "Text processing failed"
        
        return {
            "processed_text": processed_text,
            "success": success,
            "message": message,
            "id": random.randint(1000, 9999)
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing text: {str(e)}"
        )
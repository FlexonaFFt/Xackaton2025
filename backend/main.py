from fastapi import FastAPI, File, UploadFile, HTTPException
from routers import items, users
import os
import random
import PyPDF2
from docx import Document
from io import BytesIO

app = FastAPI(
    title="My FastAPI App",
    description="A clean and organized FastAPI application",
    version="1.0.0"
)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(upload_dir: str) -> str:
    while True:
        # Generate 6-digit random number
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

# Include routers
app.include_router(users.router)
app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI application!"}

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

    # Read file content
    file_content = await file.read()
    
    # Extract text based on file type
    try:
        if file.filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_content)
        else:  # docx
            extracted_text = extract_text_from_docx(file_content)
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
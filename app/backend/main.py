from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi import Request
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from routers import items, users
from routers import queries  
from sqlalchemy.orm import Session
from docx import Document
from io import BytesIO
from PIL import Image
import numpy as np
import models, database
import os, random, easyocr, PyPDF2
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from transformers import BertTokenizer, BertForSequenceClassification, pipeline, AutoModelForTokenClassification, AutoTokenizer
from sklearn.metrics import accuracy_score
from fastapi import FastAPI, HTTPException

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="My FastAPI App",
    description="A clean and organized FastAPI application",
    version="1.0.0"
)

app.include_router(queries.router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

# Урлы для frontend
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Функции для обработки файлов 
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
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(database.get_db)
):
    try:
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
            )

        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_content = await file.read()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        # Update file statistics
        file_stat = models.FileStatistics(
            file_type=file_extension,
            count=1
        )
        db.add(file_stat)
        db.commit()

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

        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            user = models.User(user_id=user_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Процесс обработки текста 
        processed_text, success = preprocess_text(extracted_text)
        is_confidential = classify_message(processed_text) or not contains_sensitive_patterns(extracted_text)
        message = {"text": extracted_text, "is_confidential": bool(is_confidential)}
        
        # Save to database
        query = models.TextQuery(
            user_id=user_id,
            original_text=extracted_text,
            processed_text=processed_text,
            success=success
        )
        db.add(query)
        db.commit()
        db.refresh(query)

        unique_filename = generate_unique_filename(upload_dir)
        file_location = os.path.join(upload_dir, unique_filename)
        
        with open(file_location, "w", encoding='utf-8') as file_object:
            file_object.write(extracted_text)
        
        return {
            "original_filename": file.filename,
            "saved_filename": unique_filename,
            "saved_location": file_location,
            "processed_text": processed_text,
            "success": success,
            "message": message,
            "is_confidential": is_confidential,
            "query_id": query.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )

# Move this line to the top level of the file, after all imports
models.Base.metadata.create_all(bind=database.engine)

class TextRequest(BaseModel):
    text: str
    user_id: str

@app.post("/process-text/")
async def process_text(
    text_request: TextRequest,
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(models.User).filter(models.User.user_id == text_request.user_id).first()
        if not user:
            user = models.User(user_id=text_request.user_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        processed_text, success = preprocess_text(text_request.text)
        is_confidential = classify_message(processed_text) or not contains_sensitive_patterns(text_request.text)
        message = {"text": text_request.text, "is_confidential": bool(is_confidential)}

        query = models.TextQuery(
            user_id=text_request.user_id,
            original_text=text_request.text,
            processed_text=processed_text,
            success=success
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        
        return {
            "processed_text": processed_text,
            "success": success,
            "message": message,
            "id": query.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing text: {str(e)}"
        )

def process_text_content(text: str) -> tuple[str, bool]:
    try:
        punctuation_marks = set('.,!?;:()[]{}«»""\'\"—–-')
        if any(char in punctuation_marks for char in text):
            return text, False
            
        processed_text = text.replace(" ", "")
        return processed_text, True
    except Exception:
        return text, False

# Функция для приведения текста к единому языку (русский)
def translate_to_russian(text):
    try:
        detected_lang = detect(text)
        if detected_lang != 'ru':
            return GoogleTranslator(source=detected_lang, target='ru').translate(text)
    except:
        pass
    return text

# Функция для нормализации текста
def preprocess_text(text):
    try:
        # Process text in chunks if it's very long
        max_chunk = 1000000  # 1MB of text at a time
        if len(text) > max_chunk:
            chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
            processed_chunks = []
            for chunk in chunks:
                chunk = chunk.lower()
                chunk = re.sub(r'[^а-яА-ЯA-Za-z0-9\s]', '', chunk)
                chunk = translate_to_russian(chunk)
                processed_chunks.append(chunk)
            return ''.join(processed_chunks), True
        else:
            text = text.lower()
            text = re.sub(r'[^а-яА-ЯA-Za-z0-9\s]', '', text)
            text = translate_to_russian(text)
            return text, True
    except Exception:
        return text, False

# Загрузка модели mBERT для классификации
tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
model = BertForSequenceClassification.from_pretrained("bert-base-multilingual-cased", num_labels=2)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Функция для классификации
def classify_message(text):
    try:
        # Split text into smaller chunks that fit within BERT's limit
        max_length = 500  # Using 500 to stay safely under the 512 token limit
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) < max_length:
                current_chunk.append(word)
                current_length += len(word)
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # If any chunk is classified as confidential, the whole text is confidential
        for chunk in chunks:
            if chunk.strip():  # Only process non-empty chunks
                result = classifier(chunk)
                if int(result[0]['label'].split('_')[-1]):
                    return 1
        return 0
    except Exception as e:
        print(f"Classification error: {str(e)}")
        return 0  # Default to non-confidential in case of error


# Функция для поиска специфичных шаблонов (email, телефон, URL)
def contains_sensitive_patterns(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\+?\d[\d -]{8,}\d"  # Простая проверка номеров
    
    if re.search(email_pattern, text) or re.search(phone_pattern, text):
        return True
    return False

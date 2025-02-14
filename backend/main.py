from fastapi import FastAPI, File, UploadFile, HTTPException
from routers import items, users
import os

app = FastAPI(
    title="My FastAPI App",
    description="A clean and organized FastAPI application",
    version="1.0.0"
)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Include routers
app.include_router(users.router)
app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI application!"}

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    # Validate file extension
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
        )

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    return {
        "filename": file.filename,
        "saved_location": file_location,
        "message": "File successfully uploaded and saved"
    }
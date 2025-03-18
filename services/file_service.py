import os
from fastapi import UploadFile
import uuid
from datetime import datetime

class FileService:
    def __init__(self):
        self.upload_dir = "static/uploads/license_plates"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_image(self, file: UploadFile) -> str:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create a path for the file
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return the relative path for database storage
        return f"/static/uploads/license_plates/{unique_filename}"

    def delete_image(self, image_path: str) -> bool:
        if not image_path:
            return True
            
        # Convert URL path to filesystem path
        file_path = os.path.join("static", image_path.lstrip("/static/"))
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False 
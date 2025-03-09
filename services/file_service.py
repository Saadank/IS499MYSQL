from fastapi import UploadFile
import os
from datetime import datetime
from typing import Optional

class FileService:
    def __init__(self, upload_dir: str = "static/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    async def save_image(self, image: Optional[UploadFile] = None) -> Optional[str]:
        if not image:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        return f"uploads/{filename}" 
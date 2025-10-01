"""File processors"""

import os
import base64
from abc import ABC, abstractmethod
from typing import Optional

import PyPDF2
import docx
from PIL import Image
import pytesseract
from openai import OpenAI

from config import Config


class BaseProcessor(ABC):
    """Base processor interface"""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def get_page_count(self, file_path: str) -> int:
        pass
    
    @abstractmethod
    def get_file_type(self) -> str:
        pass


class PDFProcessor(BaseProcessor):
    """PDF processor"""
    
    def extract_text(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def get_page_count(self, file_path: str) -> int:
        with open(file_path, 'rb') as file:
            return len(PyPDF2.PdfReader(file).pages)
    
    def get_file_type(self) -> str:
        return "pdf"


class DOCXProcessor(BaseProcessor):
    """DOCX processor"""
    
    def extract_text(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + "\n"
        
        return text.strip()
    
    def get_page_count(self, file_path: str) -> int:
        doc = docx.Document(file_path)
        return max(1, len(doc.paragraphs) // 30)
    
    def get_file_type(self) -> str:
        return "docx"


class ImageProcessor(BaseProcessor):
    """Image processor with OCR"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        self.openai_client = openai_client
    
    def extract_text(self, file_path: str) -> str:
        if self.openai_client:
            try:
                return self._extract_with_vision(file_path)
            except:
                return self._extract_with_tesseract(file_path)
        return self._extract_with_tesseract(file_path)
    
    def _extract_with_vision(self, file_path: str) -> str:
        """Extract using Vision API"""
        with open(file_path, 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        response = self.openai_client.chat.completions.create(
            model=Config.VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text from this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    
    def _extract_with_tesseract(self, file_path: str) -> str:
        """Extract using Tesseract OCR"""
        image = Image.open(file_path)
        return pytesseract.image_to_string(image).strip()
    
    def get_page_count(self, file_path: str) -> int:
        return 1
    
    def get_file_type(self) -> str:
        return "image"


class ProcessorFactory:
    """Factory to create processors"""
    
    @staticmethod
    def create(file_path: str, openai_client: Optional[OpenAI] = None) -> BaseProcessor:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return PDFProcessor()
        elif ext in ('.docx', '.doc'):
            return DOCXProcessor()
        elif ext in ('.jpg', '.jpeg', '.png'):
            return ImageProcessor(openai_client)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
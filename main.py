"""Main AI Assistant"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI

from config import Config
from models import ProcessedDocument, DocumentMetadata
from processors import ProcessorFactory
from services import AIExtractor


class DocumentProcessor:
    """Process documents"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.extractor = AIExtractor(client)
    
    def process(self, file_path: str) -> ProcessedDocument:
        """Process a document"""
        # Validate
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get processor and extract text
        processor = ProcessorFactory.create(file_path, self.client)
        raw_text = processor.extract_text(file_path)
        
        if len(raw_text.strip()) < 10:
            raise ValueError("No text extracted from document")
        
        # Extract information
        patient_info = self.extractor.extract_patient_info(raw_text)
        medical_values = self.extractor.extract_medical_values(raw_text)
        category = self.extractor.categorize_document(raw_text)
        summary = self.extractor.generate_summary(raw_text)
        
        # Create metadata
        metadata = DocumentMetadata(
            file_type=processor.get_file_type(),
            category=category,
            creation_date=datetime.now().strftime("%d/%m/%Y"),
            num_pages=processor.get_page_count(file_path),
            file_name=os.path.basename(file_path)
        )
        
        return ProcessedDocument(
            metadata=metadata,
            patient_info=patient_info,
            extracted_values=medical_values,
            summary=summary,
            raw_text=raw_text
        )


class AidaAIAssistant:
    """Main AI Assistant for Aida application"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI Assistant"""
        if api_key is None:
            api_key = Config.OPENAI_API_KEY
        
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in .env")
        
        self.client = OpenAI(api_key=api_key)
        self.processor = DocumentProcessor(self.client)
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with extracted information
        """
        try:
            result = self.processor.process(file_path)
            return result.to_dict()
        except Exception as e:
            return {
                'error': True,
                'message': str(e),
                'file_name': os.path.basename(file_path)
            }
    
    def analyze_multiple(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple documents"""
        return [self.analyze_document(fp) for fp in file_paths]
    
    def get_summary(self, file_path: str) -> str:
        """Get document summary only"""
        try:
            result = self.processor.process(file_path)
            return result.summary
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_patient_info(self, file_path: str) -> Dict[str, Optional[str]]:
        """Get patient info only"""
        try:
            result = self.processor.process(file_path)
            return result.patient_info.to_dict()
        except Exception as e:
            return {'error': str(e)}
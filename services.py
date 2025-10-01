"""AI Services"""

import json
from typing import Dict
from openai import OpenAI

from config import Config
from models import PatientInfo


class AIExtractor:
    """Extract information using AI"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def extract_patient_info(self, text: str) -> PatientInfo:
        """Extract patient information"""
        prompt = f"""
        Extract patient info from this medical document as JSON:
        {{
            "name": "full name or null",
            "date_of_birth": "DD/MM/YYYY or null",
            "address": "full address or null"
            "other_details": "any other relevant details or null"
        }}
        
        Text: {text[:Config.MAX_TEXT_LENGTH]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Extract patient info. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            return PatientInfo(
                name=data.get('name'),
                date_of_birth=data.get('date_of_birth'),
                address=data.get('address')
            )
        except:
            return PatientInfo()
    
    def extract_medical_values(self, text: str) -> Dict[str, str]:
        """Extract medical values"""
        prompt = f"""
        Extract medical measurements as JSON (with units):
        Example: {{"Blood Pressure": "120/80 mmHg", "Heart Rate": "75 bpm"}}
        
        Text: {text[:Config.MAX_TEXT_LENGTH]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Extract medical values. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {}
    
    def categorize_document(self, text: str) -> str:
        """Categorize document"""
        prompt = f"""
        Categorize this document. Choose ONE:
        - Lab Report
        - Prescription
        - Medical Record
        - Imaging Report
        - Consultation Note
        - Other
        
        Return only category name.
        Text: {text[:1000]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Categorize document."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except:
            return "Other"
    
    def generate_summary(self, text: str) -> str:
        """Generate summary"""
        prompt = f"""
        Summarize this medical document in {Config.SUMMARY_MAX_SENTENCES} sentences.
        Focus on key findings and diagnoses.
        
        Text: {text[:Config.MAX_TEXT_LENGTH]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Summarize medical documents concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except:
            return "Summary generation failed."

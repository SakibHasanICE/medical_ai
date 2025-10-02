"""AI Services with French language support"""

import json
from typing import Dict
from openai import OpenAI

from config import Config
from models import PatientInfo


class AIExtractor:
    """Extract information using AI with multilingual support"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is in French or English"""
        # Simple detection based on common French words
        french_indicators = ['le', 'la', 'les', 'du', 'de', 'à', 'est', 'et', 'un', 'une', 'des']
        text_lower = text.lower()
        
        french_count = sum(1 for word in french_indicators if f' {word} ' in text_lower)
        return 'fr' if french_count > 3 else 'en'
    
    def extract_patient_info(self, text: str) -> PatientInfo:
        """Extract patient information in English or French"""
        lang = self._detect_language(text)
        
        if lang == 'fr':
            prompt = f"""
            Extraire les informations du patient de ce document médical en tant que JSON:
            {{
                "name": "nom complet ou null",
                "date_of_birth": "date au format JJ/MM/AAAA ou null",
                "address": "adresse complète ou null"
            }}
            
            Texte: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Extraire les informations du patient. Retourner uniquement du JSON."
        else:
            prompt = f"""
            Extract patient info from this medical document as JSON:
            {{
                "name": "full name or null",
                "date_of_birth": "DD/MM/YYYY or null",
                "address": "full address or null"
            }}
            
            Text: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Extract patient info. Return only JSON."
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
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
        except Exception as e:
            print(f"Error extracting patient info: {e}")
            return PatientInfo()
    
    def extract_medical_values(self, text: str) -> Dict[str, str]:
        """Extract medical values in English or French"""
        lang = self._detect_language(text)
        
        if lang == 'fr':
            prompt = f"""
            Extraire les mesures médicales en tant que JSON (avec unités):
            Exemple: {{"Tension artérielle": "120/80 mmHg", "Fréquence cardiaque": "75 bpm"}}
            
            Texte: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Extraire les valeurs médicales. Retourner uniquement du JSON."
        else:
            prompt = f"""
            Extract medical measurements as JSON (with units):
            Example: {{"Blood Pressure": "120/80 mmHg", "Heart Rate": "75 bpm"}}
            
            Text: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Extract medical values. Return only JSON."
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error extracting medical values: {e}")
            return {}
    
    def categorize_document(self, text: str) -> str:
        """Categorize document in English or French"""
        lang = self._detect_language(text)
        
        if lang == 'fr':
            prompt = f"""
            Catégoriser ce document. Choisir UNE catégorie:
            - Rapport de Laboratoire
            - Ordonnance
            - Dossier Médical
            - Rapport d'Imagerie
            - Note de Consultation
            - Autre
            
            Retourner uniquement le nom de la catégorie.
            Texte: {text[:1000]}
            """
            system_msg = "Catégoriser le document."
        else:
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
            system_msg = "Categorize document."
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error categorizing document: {e}")
            return "Other" if lang == 'en' else "Autre"
    
    def generate_summary(self, text: str) -> str:
        """Generate summary in English or French"""
        lang = self._detect_language(text)
        
        if lang == 'fr':
            prompt = f"""
            Vous êtes un assistant spécialisé dans la synthèse de documents médicaux.
            Votre tâche est de lire attentivement les documents cliniques/médicaux et de
            générer un résumé en {Config.SUMMARY_MAX_SENTENCES} phrases.

            Directives :
            - Concentrez-vous strictement sur les constatations clés, les diagnostics et les
            informations cliniquement pertinentes.
            - Rédigez sous forme de paragraphes descriptifs complets (pas de phrases trop
            courtes ni de listes simplifiées).
            - Évitez les détails administratifs, les répétitions ou les informations
            non pertinentes.
            - Assurez l’exactitude, la clarté et un style professionnel semblable à celui
            d’un compte rendu médical ou d’un résumé de sortie hospitalière.
            
            Texte: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Résumer les documents médicaux de manière concise."
            error_msg = "Échec de la génération du résumé."
        else:
            prompt = f"""
            You are a medical document summarization assistant.
            Your task is to carefully read clinical/medical documents and generate a summary
            in {Config.SUMMARY_MAX_SENTENCES} sentences.

            Guidelines:
            - Focus strictly on key findings, diagnoses, and clinically relevant details.
            - Write in clear, descriptive paragraphs (not overly short), using professional
            medical language.
            - Avoid unnecessary administrative details, repetitions, or irrelevant commentary.
            - Ensure accuracy, conciseness, and a style similar to a physician’s chart note
            or discharge summary.
            
            Text: {text[:Config.MAX_TEXT_LENGTH]}
            """
            system_msg = "Summarize medical documents concisely."
            error_msg = "Summary generation failed."
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return error_msg
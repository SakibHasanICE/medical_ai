"""Aida AI Document Processing System"""

__version__ = "1.0.0"

from .main import AidaAIAssistant
from .models import ProcessedDocument, PatientInfo, DocumentMetadata

__all__ = ['AidaAIAssistant', 'ProcessedDocument', 'PatientInfo', 'DocumentMetadata']
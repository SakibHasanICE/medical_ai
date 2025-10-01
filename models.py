"""Data models"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any


@dataclass
class PatientInfo:
    """Patient information"""
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        return asdict(self)


@dataclass
class DocumentMetadata:
    """Document metadata"""
    file_type: str
    category: str
    creation_date: str
    num_pages: int
    file_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessedDocument:
    """Processed document result"""
    metadata: DocumentMetadata
    patient_info: PatientInfo
    extracted_values: Dict[str, str]
    summary: str
    raw_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metadata': self.metadata.to_dict(),
            'patient_info': self.patient_info.to_dict(),
            'extracted_values': self.extracted_values,
            'summary': self.summary,
            'raw_text': self.raw_text
        }

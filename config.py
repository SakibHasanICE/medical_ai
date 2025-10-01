"""Application configuration"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Models
    CHAT_MODEL = os.getenv('CHAT_MODEL', 'gpt-4o-mini')
    VISION_MODEL = os.getenv('VISION_MODEL', 'gpt-4o-mini')
    
    # Settings
    MAX_TEXT_LENGTH = 3000
    SUMMARY_MAX_SENTENCES = 15
    TEMPERATURE = 0.3
    
    # File Support
    SUPPORTED_EXTENSIONS = ('.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png')
    MAX_FILE_SIZE_MB = 50
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in .env file")
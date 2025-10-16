"""Application configuration using pydantic-settings"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings from environment variables with sensible defaults"""
    
    # LLM Configuration
    llm_provider: Literal["ollama", "openai"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    
    # OpenAI Configuration (optional)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Paths (defaults work for both Docker and local)
    catalog_path: str = "./data/product_catalog.json"
    faq_path: str = "./data/faq.txt"
    crm_storage_path: str = "./data/crm_leads.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()

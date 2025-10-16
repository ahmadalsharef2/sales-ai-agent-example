"""
Sales AI Agent - FastAPI Application

"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Sales AI Agent",
    description="Conversational AI agent for bike shop sales and customer support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (allow all origins for development) For production allow only user interface(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "status": "running",
        "service": "Sales AI Agent",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "model": settings.ollama_model if settings.llm_provider == "ollama" else settings.openai_model,
        "endpoints": {
            "chat": "/api/chat",
            "create_lead": "/api/ctream-crm/api/v1/leads",
            "create_appointment": "/api/ctream-crm/api/v1/appointments",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("Sales AI Agent Starting...")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    
    if settings.llm_provider == "ollama":
        logger.info(f"Ollama URL: {settings.ollama_base_url}")
        logger.info(f"Ollama Model: {settings.ollama_model}")
    else:
        logger.info(f"OpenAI Model: {settings.openai_model}")
    
    logger.info(f"Catalog: {settings.catalog_path}")
    logger.info(f"FAQ: {settings.faq_path}")
    logger.info(f"CRM Storage: {settings.crm_storage_path}")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Sales AI Agent shutting down...")

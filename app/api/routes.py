"""API Routes - REST endpoints for the Sales AI Agent"""
import logging
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    LeadData,
    LeadResponse,
    AppointmentRequest,
    AppointmentResponse
)
from app.services.conversation_service import conversation_manager
from app.services.crm_service import crm_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# ============================================================================
# CHAT ENDPOINT - Main conversation interface
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for customer conversations.
    
    - Handles product recommendations
    - Answers FAQ questions
    - Detects interest and collects lead information
    - Maintains conversation context
    """
    try:
        result = conversation_manager.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your message. Please try again."
        )


# ============================================================================
# CRM ENDPOINTS - Mock internal CRM API
# ============================================================================

@router.post("/ctream-crm/api/v1/leads", response_model=LeadResponse)
async def create_lead(lead_data: LeadData):
    """
    Create a new lead in the CRM system.
    
    This is a mock internal API endpoint.
    In production, this would be a separate service.
    """
    try:
        # Check if lead already exists
        existing_lead = crm_service.get_lead_by_email(lead_data.email)
        if existing_lead:
            return LeadResponse(
                lead_id=existing_lead["lead_id"],
                message="Lead already exists"
            )
        
        # Create new lead
        lead = crm_service.create_lead(
            name=lead_data.name,
            email=lead_data.email,
            phone=lead_data.phone
        )
        
        return LeadResponse(
            lead_id=lead["lead_id"],
            message="Lead created successfully"
        )
    
    except Exception as e:
        logger.error(f"Lead creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating lead"
        )


@router.post("/ctream-crm/api/v1/appointments", response_model=AppointmentResponse)
async def create_appointment(appointment_request: AppointmentRequest):
    """
    Create an appointment (optional feature - OUT OF SCOPE).
    
    This is a mock internal API endpoint.
    """
    try:
        appointment = crm_service.create_appointment(
            conversation_id=appointment_request.conversation_id,
            customer_id=appointment_request.customer_id
        )
        
        return AppointmentResponse(
            appointment_id=appointment["appointment_id"],
            message="Appointment scheduled successfully"
        )
    
    except Exception as e:
        logger.error(f"Appointment creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating appointment"
        )

# I want endpoint for speech to text
from faster_whisper import WhisperModel
from TTS.api import TTS
import tempfile
import os
import torch
from fastapi.responses import StreamingResponse

# Load Whisper model (faster-whisper)
whisper_model = WhisperModel("base", device="cuda" if torch.cuda.is_available() else "cpu", compute_type="int8")
# Load Coqui TTS model
coqui_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=torch.cuda.is_available())

@router.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Convert speech audio data to text.
    
    This is a mock endpoint for speech-to-text conversion.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        segments, info = whisper_model.transcribe(tmp_path)
        transcript = " ".join([seg.text for seg in segments])
        os.remove(tmp_path)
        return {"transcription": transcript}
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error converting speech to text"
        )

@router.post("/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    """
    Convert text to speech audio data.
    
    This is a mock endpoint for text-to-speech conversion.
    """
    try:
        wav = coqui_tts.tts(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            coqui_tts.save_wav(wav, tmp.name)
            tmp.seek(0)
            audio_bytes = tmp.read()
        os.remove(tmp.name)
        return StreamingResponse(iter([audio_bytes]), media_type="audio/wav")
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error converting text to speech"
        )

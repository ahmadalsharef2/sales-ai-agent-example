"""API Routes - REST endpoints for the Sales AI Agent"""
import logging
from fastapi import APIRouter, HTTPException, status

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


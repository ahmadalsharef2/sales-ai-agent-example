"""Pydantic models for request/response validation"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat endpoint request"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Chat endpoint response"""
    response: str = Field(..., description="Agent response")
    conversation_id: str = Field(..., description="Conversation ID")
    detected_interest: bool = Field(False, description="Whether user interest was detected")
    needs_info: Optional[List[str]] = Field(None, description="Missing user info fields")


class LeadData(BaseModel):
    """Lead information for CRM"""
    name: str = Field(..., min_length=2, description="Customer name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., min_length=5, description="Customer phone number")


class LeadResponse(BaseModel):
    """CRM Lead creation response"""
    lead_id: str = Field(..., description="Created lead ID")
    message: str = Field(..., description="Success message")


class BikeProduct(BaseModel):
    """Bike product from catalog"""
    id: int
    name: str
    type: str
    brand: str
    price_eur: int
    frame_material: str
    suspension: str
    wheel_size: int
    gears: int
    brakes: str
    weight_kg: float
    intended_use: List[str]
    color: str


class AppointmentRequest(BaseModel):
    """Appointment booking request (optional feature)"""
    conversation_id: str
    customer_id: str


class AppointmentResponse(BaseModel):
    """Appointment booking response"""
    appointment_id: str
    message: str

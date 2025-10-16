"""CRM Service - Mock internal CRM API for lead and appointment management"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import uuid

from app.utils.config import settings

logger = logging.getLogger(__name__)


class CRMService:
    """
    Mock CRM service that stores leads in a JSON file.
    In production, this would call a real CRM API.
    """
    
    def __init__(self):
        self.storage_path = Path(settings.crm_storage_path)
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage directory and file if they don't exist"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.storage_path.exists():
            # Create with one mock example
            mock_data = {
                "leads": [
                    {
                        "lead_id": str(uuid.uuid4()),
                        "name": "John Doe (Example)",
                        "email": "john.doe@example.com",
                        "phone": "+1-555-0100",
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "new",
                        "notes": "This is an example lead created on system startup"
                    }
                ],
                "appointments": []
            }
            self._save_data(mock_data)
            logger.info("Created CRM storage with example lead")
    
    def _load_data(self) -> Dict[str, List]:
        """Load data from JSON file"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading CRM data: {e}")
            return {"leads": [], "appointments": []}
    
    def _save_data(self, data: Dict[str, List]):
        """Save data to JSON file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving CRM data: {e}")
            raise
    
    def create_lead(self, name: str, email: str, phone: str) -> Dict[str, Any]:
        """
        Create a new lead in the CRM system.
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone number
        
        Returns:
            Created lead with ID and metadata
        """
        data = self._load_data()
        
        lead = {
            "lead_id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "phone": phone,
            "created_at": datetime.utcnow().isoformat(),
            "status": "new"
        }
        
        data["leads"].append(lead)
        self._save_data(data)
        
        logger.info(f"Lead created: {lead['lead_id']} - {name}")
        return lead
    
    def get_lead_by_email(self, email: str) -> Dict[str, Any] | None:
        """Find a lead by email address"""
        data = self._load_data()
        
        for lead in data["leads"]:
            if lead["email"].lower() == email.lower():
                return lead
        
        return None
    
    def create_appointment(
        self,
        conversation_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Create an appointment (optional feature).
        
        Args:
            conversation_id: ID of the conversation
            customer_id: ID of the customer (lead_id)
        
        Returns:
            Created appointment with ID and metadata
        """
        data = self._load_data()
        
        appointment = {
            "appointment_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "customer_id": customer_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
        data["appointments"].append(appointment)
        self._save_data(data)
        
        logger.info(f"Appointment created: {appointment['appointment_id']}")
        return appointment
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        """Get all leads (for debugging/testing)"""
        data = self._load_data()
        return data["leads"]
    
    def get_all_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments (for debugging/testing)"""
        data = self._load_data()
        return data["appointments"]


# Singleton instance
crm_service = CRMService()

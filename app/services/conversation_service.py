"""Conversation Manager - Simplified single-class design"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import re

from app.services.llm_service import llm_service
from app.services.data_service import DataService
from app.services.crm_service import crm_service
from app.utils.config import settings
from app.utils.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Simplified Conversation Manager - Single class design.
    
    Philosophy: Let the LLM handle ALL routing and detection.
    We just provide context (products + FAQ) and extract contact info.
    """
    
    def __init__(self):
        # Service dependencies
        self.data_service = DataService(
            catalog_path=settings.catalog_path,
            faq_path=settings.faq_path
        )
        
        # Conversation storage: conversation_id -> state dict
        self.conversations: Dict[str, Dict] = {}
    
    def _init_conversation(self, conversation_id: str) -> Dict:
        """Initialize a new conversation state"""
        return {
            "conversation_id": conversation_id,
            "messages": [],
            "interest_detected": False,
            "lead_data": {"name": None, "email": None, "phone": None},
            "lead_created": False,
            "created_at": datetime.utcnow()
        }
    
    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> Dict:
        """Get existing conversation or create new one"""
        if conversation_id and conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Create new conversation
        new_id = conversation_id or str(uuid.uuid4())
        conv = self._init_conversation(new_id)
        self.conversations[new_id] = conv
        
        logger.info(f"New conversation created: {new_id}")
        return conv
    
    def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Process user message and generate response.
        Simplified: Let LLM handle all routing and detection.
        
        Returns:
            Dictionary with response, conversation_id, and metadata
        """
        conv = self.get_or_create_conversation(conversation_id)
        
        # Add user message to history
        conv["messages"].append({"role": "user", "content": message})
        # Keep only the latest 5 messages
        if len(conv["messages"]) > 5:
            conv["messages"] = conv["messages"][-5:]
        
        # Try to extract lead info from every message (non-intrusive)
        self._extract_lead_info(conv, message)
        
        # If we have all lead info and haven't created lead yet, create it
        if self._has_all_lead_info(conv) and not conv["lead_created"]:
            crm_service.create_lead(
                name=conv["lead_data"]["name"],
                email=conv["lead_data"]["email"],
                phone=conv["lead_data"]["phone"]
            )
            conv["lead_created"] = True
        
        # Build context with all available data
        context_parts = []
        
        # Always include product catalog (LLM decides if relevant)
        bikes = self.data_service.search_bikes(message, max_results=5)
        if bikes:
            context_parts.append(f"Available bikes:\n{self.data_service.format_bikes_for_context(bikes)}")
        
        # Always include FAQ (LLM decides if relevant)
        faq_info = self.data_service.search_faq(message)
        if faq_info:
            context_parts.append(f"FAQ Information:\n{faq_info[:800]}")
        
        # Build single prompt with all context
        full_context = "\n\n".join(context_parts) if context_parts else ""
        
        # Use only the latest 5 messages for LLM context
        history = conv["messages"][-5:]
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if full_context:
            messages.append({"role": "user", "content": f"{full_context}\n\nCustomer: {message}"})
        messages.extend(history)
        
        # Get LLM response
        response = llm_service.chat(messages, temperature=0.7)
        
        # Add assistant response to history
        conv["messages"].append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "conversation_id": conv["conversation_id"],
            "detected_interest": conv["interest_detected"],
            "needs_info": self._get_missing_fields(conv) if not conv["lead_created"] else None
        }
    
    def _has_all_lead_info(self, conv: Dict) -> bool:
        """Check if all lead information is collected"""
        return all(value is not None for value in conv["lead_data"].values())
    
    def _get_missing_fields(self, conv: Dict) -> List[str]:
        """Get list of missing lead information fields"""
        return [key for key, value in conv["lead_data"].items() if value is None]
    
    def _extract_lead_info(self, conv: Dict, message: str):
        """Extract lead information from message using regex patterns"""
        # Extract email
        if not conv["lead_data"]["email"]:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, message)
            if email_match:
                conv["lead_data"]["email"] = email_match.group(0)
        
        # Extract phone
        if not conv["lead_data"]["phone"]:
            phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}'
            phone_match = re.search(phone_pattern, message)
            if phone_match:
                conv["lead_data"]["phone"] = phone_match.group(0)
        
        # Extract name
        if not conv["lead_data"]["name"]:
            name_patterns = [
                r"(?:my name is|i'm|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$"
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, message, re.IGNORECASE)
                if name_match:
                    conv["lead_data"]["name"] = name_match.group(1)
                    break


# Singleton instance
conversation_manager = ConversationManager()

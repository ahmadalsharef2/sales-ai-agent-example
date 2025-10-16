import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.services.crm_service import crm_service

client = TestClient(app)


class TestConversationAPI:
    """Requirement 1: Conversation API"""
    
    def test_chat_endpoint_responds(self):
        """Chat endpoint returns proper response structure"""
        start_time = time.time()
        response = client.post("/api/chat", json={"message": "Hello"})
        latency = time.time() - start_time
        print(f"\n⏱️  Chat endpoint latency: {latency:.3f}s")
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    def test_conversation_context_maintained(self):
        """Maintains context across multiple turns"""
        start_time = time.time()
        
        # Turn 1
        response1 = client.post("/api/chat", json={"message": "I need a mountain bike"})
        conv_id = response1.json()["conversation_id"]
        
        # Turn 2 - should remember we're talking about mountain bikes
        response2 = client.post("/api/chat", json={
            "message": "What's the price range?",
            "conversation_id": conv_id
        })
        
        latency = time.time() - start_time
        print(f"\n⏱️  Context retention (2 turns) latency: {latency:.3f}s")
        
        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conv_id


class TestProductRecommendation:
    """Requirement 2: Product Recommendation from Catalog"""
    
    def test_recommends_bike_by_type(self):
        """Recommends appropriate bike based on type/usage"""
        start_time = time.time()
        response = client.post("/api/chat", json={
            "message": "I need a bike for city commuting"
        })
        latency = time.time() - start_time
        print(f"\n⏱️  Product recommendation latency: {latency:.3f}s")
        
        assert response.status_code == 200
        response_text = response.json()["response"].lower()
        
        # Should mention city/urban bikes or commuter bikes
        assert any(keyword in response_text for keyword in [
            "city", "urban", "commut", "cruiser", "ecoride"
        ])
    
    def test_recommends_bike_by_budget(self):
        """Recommends bikes within budget constraints"""
        start_time = time.time()
        response = client.post("/api/chat", json={
            "message": "I want a bike under $800"
        })
        latency = time.time() - start_time
        print(f"\n⏱️  Budget-based recommendation latency: {latency:.3f}s")
        
        assert response.status_code == 200
        response_text = response.json()["response"].lower()
        
        # Should recommend affordable bikes
        assert any(keyword in response_text for keyword in [
            "cruiser", "ecoride", "budget", "affordable", "$"
        ])


class TestLeadCollection:
    """Requirement 3: Lead Collection and CRM Storage"""
    
    def test_detects_purchase_interest(self):
        """Detects when customer shows interest in purchasing"""
        start_time = time.time()
        response = client.post("/api/chat", json={
            "message": "I'm interested in buying the Urban Cruiser X"
        })
        latency = time.time() - start_time
        print(f"\n⏱️  Interest detection latency: {latency:.3f}s")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should either set detected_interest flag or ask for contact info
        response_text = data["response"].lower()
        assert (data.get("detected_interest") is True or 
                any(word in response_text for word in ["name", "email", "contact", "phone"]))
    
    def test_collects_and_stores_lead(self):
        """Collects contact info and stores in CRM"""
        start_time = time.time()
        
        # Show interest
        response1 = client.post("/api/chat", json={
            "message": "I want to purchase the TrailBlazer X1"
        })
        conv_id = response1.json()["conversation_id"]
        
        # Provide contact information
        response2 = client.post("/api/chat", json={
            "message": "My name is Sarah Connor, email sarah@test.com, phone +1-555-0199",
            "conversation_id": conv_id
        })
        
        latency = time.time() - start_time
        print(f"\n⏱️  Lead collection (full flow) latency: {latency:.3f}s")
        
        assert response2.status_code == 200
        
        # Verify lead was stored in CRM
        lead = crm_service.get_lead_by_email("sarah@test.com")
        assert lead is not None
        assert "sarah" in lead["name"].lower()


class TestFAQAnswering:
    """Requirement 4: FAQ Knowledge Base"""
    
    def test_answers_delivery_question(self):
        """Answers delivery/shipping questions from FAQ"""
        start_time = time.time()
        response = client.post("/api/chat", json={
            "message": "How long does shipping take?"
        })
        latency = time.time() - start_time
        print(f"\n⏱️  FAQ (delivery) latency: {latency:.3f}s")
        
        assert response.status_code == 200
        response_text = response.json()["response"].lower()
        
        # Should mention delivery timeframe from FAQ
        assert any(keyword in response_text for keyword in [
            "delivery", "ship", "days", "business"
        ])
    

class TestEndToEnd:
    """Integration Tests: Complete User Journeys"""
    
    def test_complete_purchase_journey(self):
        """Full journey: browse → interest → lead collection"""
        start_time = time.time()
        
        # Step 1: Ask about bikes
        response1 = client.post("/api/chat", json={
            "message": "I'm looking for a road bike"
        })
        conv_id = response1.json()["conversation_id"]
        assert "road" in response1.json()["response"].lower()
        
        # Step 2: Show interest
        response2 = client.post("/api/chat", json={
            "message": "I'm interested in buying one",
            "conversation_id": conv_id
        })
        assert response2.status_code == 200
        
        # Step 3: Provide contact info
        response3 = client.post("/api/chat", json={
            "message": "I'm Mike Ross, mike@test.com, 555-2468",
            "conversation_id": conv_id
        })
        
        latency = time.time() - start_time
        print(f"\n⏱️  Complete purchase journey (3 steps) latency: {latency:.3f}s")
        
        assert response3.status_code == 200
        
        # Verify lead in CRM
        lead = crm_service.get_lead_by_email("mike@test.com")
        assert lead is not None
    
    def test_mixed_conversation_flow(self):
        """Journey with product + FAQ questions"""
        start_time = time.time()
        
        # Ask about product
        response1 = client.post("/api/chat", json={
            "message": "What e-bikes do you have?"
        })
        conv_id = response1.json()["conversation_id"]
        
        # Ask FAQ question
        response2 = client.post("/api/chat", json={
            "message": "Do you offer financing?",
            "conversation_id": conv_id
        })
        
        # Back to product discussion
        response3 = client.post("/api/chat", json={
            "message": "I'll take the EcoRide E-City",
            "conversation_id": conv_id
        })
        
        latency = time.time() - start_time
        print(f"\n⏱️  Mixed conversation (3 turns) latency: {latency:.3f}s")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert all(r.json()["conversation_id"] == conv_id for r in [response1, response2, response3])


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_is_healthy(self):
        """Health endpoint responds"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

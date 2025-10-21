# Manual Conversation Test Cases
# Use these to test the AI agent manually via curl or chat interface

## Test Case 1: Product Recommendation (City Bike)
**You:** Hi, I need a bike for commuting to work in the city
**Expected:** Agent recommends Urban Cruiser X or EcoRide E-City with prices
**You:** What features does the Urban Cruiser have?
**Expected:** Lists features from catalog (aluminum frame, 7 gears, disc brakes, etc.)


---

## Test Case 2: Budget-Based Recommendation
**You:** I'm looking for something under $700
**Expected:** Recommends affordable options like Urban Cruiser X ($599)
**You:** Do you have anything cheaper?
**Expected:** Shows cheapest available options

---

## Test Case 3: FAQ - Delivery
**You:** How long does delivery take?
**Expected:** Mentions 5-7 business days (from FAQ)
**You:** Do you ship internationally?
**Expected:** Answers based on FAQ information


---

## Test Case 4: FAQ - Return Policy
**You:** What is your return policy?
**Expected:** 30-day return policy details from FAQ
**You:** Can I exchange instead of return?
**Expected:** Exchange policy information

---
---

## Test Case 5: Lead Collection - Step by Step
**You:** I want to purchase the TrailBlazer X1
**Expected:** Asks for your name
**You:** I'm Sarah Johnson
**Expected:** Asks for email
**You:** sarah.j@email.com
**Expected:** Asks for phone number
**You:** +1-555-8765
**Expected:** Confirms all details, lead created

---

## Test Case 6: Context Retention
**You:** Show me road bikes
**Expected:** Lists Speedster Pro and AeroRace 3000
**You:** What's the weight of the first one?
**Expected:** Remembers "first one" = Speedster Pro, gives weight (18 lbs)
**You:** And the price?
**Expected:** Still talking about Speedster Pro, gives price ($1,599)


---

## Test Case 7: Negative Case - Out of Scope
**You:** Can you help me repair my old bike?
**Expected:** Politely explains they sell bikes but may mention service FAQ
**You:** Do you sell bike helmets?
**Expected:** Explains focus is on bikes, may mention accessories if in FAQ

---

## CURL Commands for Testing:

```bash
# Test Case 1: Product Recommendation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a bike for commuting"}'

# Test Case 7: Lead Collection
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to buy the Urban Cruiser X"}'

# Follow-up (use conversation_id from previous response)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "John Smith, john@test.com, 555-1234", "conversation_id": "YOUR_CONVERSATION_ID_HERE"}'

# Test Case 4: FAQ
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How long does delivery take?"}'
```

---

## Expected Latency Benchmarks:
- Simple greeting: < 2s
- Product recommendation: 2-4s
- FAQ answer: 2-3s
- Lead collection: 2-4s
- Multi-turn (2-3 exchanges): 5-10s total

---

## What to Check:
✅ Agent recommends correct bike type (mountain/city/road/e-bike)
✅ Prices mentioned match catalog ($599-$2,899 range)
✅ FAQ answers contain correct information (delivery times, warranty, etc.)
✅ Interest detection triggers contact info collection
✅ Lead stored in data/crm_leads.json with correct fields
✅ Conversation_id stays same across turns
✅ Context retained (agent remembers previous messages)
✅ Responses under 150 words (as per prompt)
✅ Tone is friendly and helpful

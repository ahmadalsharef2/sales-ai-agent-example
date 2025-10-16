
## Key Decisions


### 0. Ramazan call & Readme notes:

ChatBot API that acts as a Sales AI Agent  for an online bike shop.
Conduct customer consultations via an API (REST or WebSocket).
Recommend products from a given product catalog and Answer FAQ.
Detect customer interest and guide the conversation.
Collect customer details (name, email, phone number) when interest is confirmed.
Create a Lead in the internal CRM system (internal)

knowledge base: .json product catalog & faq
scalability: docker
flexibility: locall llm or openai api
AI practices: Prompting, RAG, Vector Search (optional)

backend only, added streamlit as extra and for easier self-testing and monirtoring

CRM explaination: as sales, to have followup. CRM lead is to store client contact information for further contact. on interest -> collect usr data -> store in josn. but over api, internally

create side branch: fast api, python, no streaming needed.


### 1. API Architecture
**Decision**: REST API, for chat also rest api over websocket (as websocket more complex, better for real-time but overkill, REST is easier when no streaming required)  
**Rationale**: Simpler to implement, easier to test/assess, standard approach.  

### 2. LLM Model Selection
**Decision**: Llama 3.2 1B ✅  over Gemma 3 1B and Llama 3.2 3B
**Rationale**: 
- Fast and efficient for structured data (FAQ + catalog)
- 1B sufficient for ~20 bikes + small FAQ ( I used used quantized 3B previously for 40-endpoint agent, overkill here)
- Meta official model, reliable, licensing okay
- Optional: OpenAI API (configurable fallback via .env)
- Flexibility: Switch between providers without code changes

### 3. Project Structure
```
app/
├── main.py              # FastAPI entry point
├── api/routes.py        # API endpoints
├── services/
│   ├── llm_service.py   # LLM interaction logic
│   ├── rag_service.py   # Vector search + retrieval
│   └── crm_service.py   # CRM API calls (mock)
│   └── conversation_service.py   
├── models/schemas.py    # Pydantic models for request/response validation
└── utils/prompts.py     # Prompt templates for different conversation stages
```

**Should prompts be hardcoded?** Mix - Base templates in code, configurable parameters via config, can be modified, tested in real-time in Streamlit GUI


---



## How to Start

1. **Copy env file**: `cp .env.example .env`
2. **Run with Docker**: `docker-compose up`
3. **Or local dev**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

---


### Key Decisions Made

#### 1. **First thougths** ✅

I thought it like

input - llm - RAG - output

Modules
conversation, llm, data

best practices:
fastapi examples on github


Made trade-offs for small-scale requirements
Focused on clean architecture with minimal complexity
Services pattern with clear separation of concerns

Let the LLM handle intent detection rather than rule-based logic
System prompt includes clear instructions for lead collection
Single conversation flow rather than complex state machines

Containerized for reproducibility (FastAPI + Ollama)
Persisted models in Docker volume (avoids re-downloads)
Testing: Both automated (pytest) and manual (Streamlit UI)


#### 2. **Linear Search vs Vector DB** ✅

🎯 Vector DB / RAG - Do We Need It?
NO,  will use linear search
Here's why:

For Data Size:
📊 Product Catalog: ~15-20 bikes (238 lines JSON)
📄 FAQ: ~30 questions (small text file)
Total: < 500KB of text

✅ Simple approach works: Load JSON + FAQ into memory, filter with basic logic
✅ LLM context window: Llama 3.2 1B can handle ~8K tokens ( entire dataset fits!)

❌ Vector DB overkill: For <50 items, linear search is faster than embeddings. (Vector DB can be used for over 500 items).


Note: RAG source faq or product, general or product question

#### 3. **Ollama in Docker** ✅
**Setup**: 
- Ollama service pulls `llama3.2:1b` on startup
- FastAPI app connects to `http://ollama:11434`
- No local Ollama installation needed
- Run with: `docker-compose up`


#### 4. **Why This Folder Structure?** ✅


Separation of Concerns: Routes → Services → Data (clear flow)
Testable: Easy to test services independently
Scalable: Add new features without touching existing code
FastAPI Convention: Most FastAPI projects follow this
Clean Dependencies: Routes call services, services call data/external APIs


Alternative (simpler but less scalable):
app.py  # Everything in one file (OK for tiny apps)


#### 5. Why NOT use pip freeze:
Pros of pip freeze:

Captures exact versions of ALL dependencies (including sub-dependencies)
Reproducible builds
Cons of pip freeze:

❌ Messy: 50+ packages (including sub-dependencies we don't care about)
❌ Hard to read: Can't see what we actually need
❌ Harder to upgrade: If we want to update fastapi, we need to figure out which 10 sub-packages to update too
❌ Platform-specific: May include OS-specific 

This project uses venv to not conflict with global Python setup for development environment

## How It Works (Request Flow)

```
User → POST /api/chat
  ↓
routes.py (API layer)
  ↓
conversation_service.py (business logic)
  └→ conversation_service.py 
  ├→ Detect stage: Product? FAQ? Lead collection?
  ├→ data_service.py (search bikes/FAQ)
  ├→ llm_service.py (generate response)
  └→ crm_service.py (store lead when ready)
  ↓
Return ChatResponse to user
```
source venv/bin/activate && streamlit run chat_ui.py --server.headless=true


## Concerns on Production 
Ports hardcoded
Datapaths hardcoded
CORS open to all
for production ROGUE or BELU
monitor performance -> mlflow

no conversations state in memory or DB
no thread-safe
process message function is long
do i need step-by-setp prompting? for CRM lead?
crm_lead data in gitignore for gdpr policy
average latency is 7 seconds (including tiem to write response, except first query). Can be done into 5 or less.
Thread safety for conversation state
Database persistence instead of in-memory storage
Improved performance monitoring
Appointment scheduling feature



# First time setup
mkdir -p data
touch data/crm_leads.json
echo '{"leads":[],"appointments":[]}' > data/crm_leads.json

# Then start services
docker-compose up -d
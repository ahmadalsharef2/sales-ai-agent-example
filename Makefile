install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	streamlit run chat_ui.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

test:
	pytest tests/ -v

# Pull Ollama model for local use
pull-model:
	ollama pull llama3.2:1b

.PHONY: install run ui docker-up docker-down test pull-model

# CogniFlow AI Tutor Service

This microservice provides AI-powered tutoring features:
- Conversational AI chat
- Spaced repetition scheduling
- Adaptive content suggestions

## Features
- In-memory (no-db) mode for development
- Production-ready code (commented)
- REST API endpoints
- Modular, well-documented code

## Endpoints
- `POST /ai/chat` — Conversational AI chat
- `POST /ai/spaced-repetition` — Spaced repetition scheduling
- `POST /ai/adaptive-content` — Adaptive content suggestions
- `GET /health` — Health check

## Dev Mode
Set `NO_DATABASE_MODE=true` (default) to use in-memory storage and stubbed AI logic.

## Production Mode
Set `NO_DATABASE_MODE=false` and implement integrations (see commented code).

## Running Locally
```sh
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8006
```

## Docker
A Dockerfile is provided for containerized deployment.

## Extending
- Integrate with OpenAI/HuggingFace for real AI
- Add persistent storage (PostgreSQL, Redis)
- Implement advanced spaced repetition algorithms
- Connect to user/courses/analytics services

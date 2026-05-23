# CodeForge AI

CodeForge AI is an AI-assisted software engineering project built to help developers simplify common development tasks such as code review, debugging, documentation, and development support.

The idea behind this project is to reduce repetitive work and provide developers with intelligent assistance during different stages of software development.

---

## Features Implemented

### Code Review Module
- Accept code input from users
- Analyze code using backend logic
- Generate code quality scores
- Detect common issues
- Provide improvement suggestions

### Backend Architecture
- Modular FastAPI backend structure
- Separate routes, models, and services
- API-based communication between frontend and backend

---

## Tech Stack

### Frontend
- React
- Vite
- Axios

### Backend
- FastAPI
- Python

### Database
- PostgreSQL

---

## Project Structure

```text
codeforge-ai/

backend/
├── models/
├── routes/
├── services/
├── utils/
└── main.py

frontend/
├── components/
├── styles/
└── src/
```

---

## Current Workflow

```text
User submits code
        ↓
Frontend sends request
        ↓
FastAPI backend receives request
        ↓
Code analysis logic processes input
        ↓
Results generated
        ↓
Response displayed to user
```

---

## Planned Enhancements

### AI Features
- LLM-powered code analysis
- Context-aware suggestions
- RAG-based project understanding

### Developer Tools
- CI/CD log debugging
- Documentation generation
- Test case generation
- GitHub integration

### Platform Features
- Authentication system
- User history and saved reports
- Dashboard for analytics

---

## Current State

The foundational architecture and Code Review module have been implemented. The project is currently being expanded with additional AI-powered features.

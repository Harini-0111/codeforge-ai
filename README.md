# CodeForge AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

CodeForge AI is an AI-powered developer tool for reviewing code and analyzing software projects. It supports code snippets, local folders, ZIP archives, and public GitHub repositories through a shared analysis pipeline.

The current focus is code review and multi-source project analysis. Repository-Aware RAG is the next planned milestone.

---

## Features

### Implemented

#### Code Review
- AI-powered code review
- Review history

#### Project Analysis
- Local folder analysis
- ZIP upload analysis
- Public GitHub repository analysis
- Project Scanner
- Shared Analysis Pipeline
- SQLite persistence

#### GitHub Support
- Branch and tag selection
- Commit SHA resolution
- Repository metadata retrieval

### Next

- Repository-Aware RAG
- Pull Request Review
- Authentication
- Deployment

---

## Architecture

```text
               CodeForge AI

 Local Folder   ZIP Upload   GitHub Repository
         \          |          /
          \         |         /
           +--------+--------+
                    |
             Source Adapter
                    |
      Shared Analysis Pipeline
                    |
           Project Scanner
                    |
             Project Map
                    |
          AI Project Review
                    |
        SQLite Persistence
                    |
         History & Dashboard
```

---

## Tech Stack

### Frontend

- React
- Vite
- Axios

### Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- HTTPX
- OpenRouter API

### Database

- SQLite

---

## Project Structure

```text
codeforge-ai/
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── database.py
│   └── main.py
│
└── frontend/
    ├── src/
    ├── public/
    └── package.json
```

---

## Getting Started

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Set the `OPENROUTER_API_KEY` environment variable before starting the backend.

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## API

| Method | Endpoint |
|---------|----------|
| POST | `/api/review` |
| GET | `/api/reviews` |
| GET | `/api/reviews/{id}` |
| POST | `/api/projects/scan` |
| POST | `/api/projects/upload` |
| POST | `/api/projects/github` |

---

## Roadmap

- Repository-Aware RAG
- Repository-aware search
- Pull Request Review
- Authentication
- Deployment

---

## Contributing

Contributions are welcome.

Please keep new features aligned with the existing architecture:

- Keep the Project Scanner source-independent.
- Route new project sources through the Source Adapter layer.
- Reuse the Shared Analysis Pipeline whenever possible.

---

## License

MIT License

---

**Built by Harini Patsa**

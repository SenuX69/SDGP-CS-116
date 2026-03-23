# PathFinder — Resume Scanner & Analyzer

A full-stack resume scanning and analysis tool built with **FastAPI** and **Next.js**.  
Upload a PDF or DOCX resume and get structured data, skill matching, and actionable suggestions instantly.

---

## Features

- Upload PDF or DOCX resume files
- Extracts personal details — name, email, phone, links
- Detects and parses resume sections — summary, experience, education, skills, projects, certifications
- Normalizes and ranks skills against a canonical skill map
- Structured experience and education entry parsing with date detection
- Resume analyzer that matches skills against commonly required core skills
- Generates actionable improvement suggestions
- Downloads a formatted `.txt` report of the scan results
- Clean REST API with error handling and path traversal protection

---

## Tech Stack

**Backend**
- Python 3.11
- FastAPI
- pdfplumber — PDF text extraction
- python-docx — DOCX text extraction
- Uvicorn — ASGI server

**Frontend**
- Next.js 14
- React 18
- Tailwind CSS

---


## Project Structure

```
project/
├── backend/
    ├── main.py              # FastAPI app — all endpoints and logic
    ├── requirements.txt     # Python dependencies
    └── outputs/             # Generated scan report .txt files

```

## Getting Started

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

---

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:3000`  
Resume scanner page at `http://localhost:3000/resume`


## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/scan` | Upload a PDF or DOCX resume for scanning |
| `GET` | `/download/{filename}` | Download the generated `.txt` report |
| `GET` | `/health` | Check if the backend server is running |

## Supported File Types

- `.pdf`
- `.docx`
- `.doc`

---

## Requirements

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9
pdfplumber==0.11.0
python-docx==1.1.2
```

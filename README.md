# ElectraLens - Voter Management System

This project provides a comprehensive Voter Management System with FastAPI backend, PostgreSQL/SQLite database, and a Streamlit frontend with advanced filtering and analytics.

Quick start (Windows PowerShell):

1. Create and activate a virtual environment

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the backend API

```powershell
uvicorn app.main:app --reload --port 8000
```

3. Start the Streamlit frontend

```powershell
streamlit run streamlit_app.py
```

Files:
- `app/` - FastAPI backend
- `extract/` - PDF/CSV extraction and cleaning
- `streamlit_app.py` - Streamlit dashboard frontend
- `requirements.txt` - Python dependencies

Notes:
- By default this uses SQLite for quick setup. To use PostgreSQL, set DATABASE_URL env var (e.g. postgresql+psycopg2://user:pass@host/dbname).

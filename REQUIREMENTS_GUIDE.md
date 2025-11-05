# 📁 Requirements Files Guide

## File Structure Overview

```
ElectraLens/
├── requirements.txt              # 📱 STREAMLIT CLOUD (Frontend only)
├── requirements-backend.txt      # ⚙️  BACKEND ONLY (FastAPI + DB)
├── requirements-vercel.txt       # 🚀 VERCEL DEPLOYMENT (API)
├── .python-version              # 🐍 Python 3.11 for Streamlit Cloud
└── streamlit_app.py             # 📊 Main Streamlit application
```

## Deployment Guide

### 🎯 Streamlit Cloud (Frontend)
- **File**: `requirements.txt` (NO database drivers)
- **Python**: 3.11 (specified in `.python-version`)
- **Purpose**: Pure frontend dashboard
- **Dependencies**: streamlit, requests, pandas, plotly

### 🚀 Vercel (API Backend)  
- **File**: `requirements-vercel.txt` (WITH database drivers)
- **Purpose**: FastAPI backend with database
- **Dependencies**: fastapi, sqlalchemy, psycopg2-binary

### 🖥️ Local Development
- **File**: `requirements-backend.txt` (Full backend)
- **Purpose**: Complete local development environment

## Why This Structure?

**Problem**: `psycopg2-binary` fails on Streamlit Cloud Python 3.13
**Solution**: Separate requirements files for different deployment targets

✅ **Streamlit Cloud**: Clean frontend-only dependencies
✅ **Vercel**: Backend with database drivers  
✅ **Local**: Full development environment

## Quick Deploy Commands

```bash
# Deploy Streamlit Frontend
# 1. Push to GitHub (uses requirements.txt automatically)
git push origin main

# 2. Deploy on share.streamlit.io
# Repository: datavineo/ElectraLens
# Branch: main
# Main file: streamlit_app.py

# Deploy Vercel Backend (already working)
# Uses requirements-vercel.txt automatically
# URL: https://electra-lens.vercel.app
```
# Vercel-compatible extractor with minimal dependencies
import os
from typing import List

def process_uploaded_pdf(*args, **kwargs):
    """Fallback function for PDF processing when pdfplumber is not available"""
    return {
        "message": "PDF processing not available in serverless environment",
        "status": "disabled"
    }

def load_csv_into_db(*args, **kwargs):
    """Fallback function for CSV processing"""
    return {
        "message": "CSV processing available via API endpoints",
        "status": "api_only"
    }
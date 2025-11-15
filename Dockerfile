FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-streamlit.txt .
RUN pip install --no-cache-dir -r requirements-streamlit.txt

# Copy application files
COPY . .

# Create .streamlit directory if it doesn't exist
RUN mkdir -p .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
# Streamlit Deployment Guide for ElectraLens

## Option 1: Streamlit Community Cloud (Recommended)

### Prerequisites
- GitHub repository (✅ Already done: datavineo/ElectraLens)
- Streamlit app file (✅ Already done: streamlit_app.py)
- Requirements file (✅ Already done: requirements-streamlit.txt)

### Deployment Steps

1. **Visit Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select repository: `datavineo/ElectraLens`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - App URL: Choose a custom name (e.g., `electralens-voter-analysis`)

3. **Configure Environment Variables**
   In the Advanced settings, add:
   ```
   API_BASE = "https://your-vercel-api-url.vercel.app"
   ```
   Replace with your actual Vercel API URL.

4. **Deploy**
   - Click "Deploy!"
   - Wait for the build to complete

### Configuration Files Already Set Up
- ✅ `.streamlit/config.toml` - App configuration
- ✅ `requirements-streamlit.txt` - Dependencies
- ✅ `streamlit_app.py` - Main application

---

## Option 2: Heroku (Paid Platform)

### Additional Files Needed
Create these files for Heroku deployment:

**Procfile:**
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.11.0
```

### Deployment Steps
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. Set environment variables: `heroku config:set API_BASE=your-api-url`

---

## Option 3: Railway (Alternative Platform)

### Steps
1. Visit https://railway.app/
2. Connect GitHub repository
3. Deploy from `main` branch
4. Set environment variables in Railway dashboard

---

## Option 4: Docker + Any Cloud Provider

### Dockerfile (create if needed):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-streamlit.txt .
RUN pip install -r requirements-streamlit.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
```

---

## Post-Deployment Checklist

1. ✅ Verify Streamlit app loads without errors
2. ✅ Test API connectivity to your Vercel backend
3. ✅ Test all features: voter upload, analysis, charts
4. ✅ Verify responsive design on mobile devices
5. ✅ Check performance with sample data

---

## Troubleshooting

### Common Issues:
1. **Module not found**: Check requirements-streamlit.txt
2. **API connection failed**: Verify API_BASE environment variable
3. **Slow loading**: Optimize data processing and caching

### Debug Commands:
```bash
# Local testing
streamlit run streamlit_app.py

# Check dependencies
pip freeze > current-requirements.txt
```

---

## Security Notes

- Never commit secrets.toml to GitHub
- Use environment variables for sensitive data
- Configure CORS properly for production API
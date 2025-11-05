# 🚀 Vercel Deployment Guide - ElectraLens

## Complete Step-by-Step Guide for Production Deployment

---

## 📋 Pre-Deployment Checklist

### ✅ What's Ready:
- [x] FastAPI backend configured (`app/main.py`)
- [x] Vercel serverless entry point (`api/index.py`)
- [x] Vercel configuration (`vercel.json`)
- [x] SQLite in-memory database for demo
- [x] Rate limiting and CORS configured
- [x] Logging setup
- [x] Authentication system

### ⚠️ Critical Items to Fix Before Deployment:

1. **Create `requirements.txt`** (currently missing)
2. **Fix database configuration** to support production PostgreSQL
3. **Add missing dependencies** (slowapi, streamlit packages)
4. **Set up Vercel environment variables**
5. **Deploy Streamlit separately** (Streamlit Cloud recommended)

---

## 🔧 STEP 1: Fix Code Issues (Required Before Deploy)

### 1.1 Create `requirements.txt`

Create a file at the root: `requirements.txt`

```txt
# Backend Core
fastapi==0.121.0
uvicorn[standard]==0.38.0
sqlalchemy==2.0.44
pydantic==2.12.3
python-multipart==0.0.6
python-dotenv==1.0.0
passlib[bcrypt]==1.7.4

# Rate Limiting
slowapi==0.1.9

# Streamlit Frontend (optional - deploy separately)
streamlit==1.29.0
requests==2.31.0
pandas==2.2.2
plotly==5.20.0

# Database drivers (if using PostgreSQL)
psycopg2-binary==2.9.9
```

### 1.2 Fix Database Configuration

**File: `app/database.py`**

Current issue: Code ignores `DATABASE_URL` when `VERCEL` is set.

**Replace lines 13-19 with:**

```python
# Prefer DATABASE_URL from environment (for production PostgreSQL)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    # Fallback: Use in-memory SQLite on Vercel, file-based locally
    if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
        DATABASE_URL = 'sqlite:///:memory:'
    else:
        DATABASE_URL = 'sqlite:///./voters.db'
```

---

## 🌐 STEP 2: Deploy Backend to Vercel

### 2.1 Connect to Vercel

1. Go to https://vercel.com/dashboard
2. Click **"New Project"**
3. Import from GitHub: `datavineo/ElectraLens`
4. Select your repository and click **"Import"**

### 2.2 Configure Build Settings

In Vercel project settings:

- **Framework Preset:** Other
- **Build Command:** (leave empty)
- **Output Directory:** (leave empty)
- **Install Command:** `pip install -r requirements.txt`
- **Root Directory:** `./` (root of repo)

### 2.3 Set Environment Variables

Go to: **Project Settings → Environment Variables**

Add the following variables (all environments: Production, Preview, Development):

#### Required Environment Variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/dbname?sslmode=require` | Production PostgreSQL URL (see below for setup) |
| `ALLOWED_ORIGINS` | `https://your-streamlit-app.streamlit.app,http://localhost:8501` | Comma-separated frontend URLs |
| `LOG_LEVEL` | `INFO` | Logging level |
| `VERCEL` | `1` | Automatically set by Vercel |
| `VERCEL_ENV` | `production` | Automatically set by Vercel |

### 2.4 Set Up Production Database (PostgreSQL)

**Option A: Neon (Recommended - Free Tier Available)**

1. Go to https://neon.tech/
2. Create free account
3. Create new project: "ElectraLens DB"
4. Copy connection string (looks like):
   ```
   postgresql://user:password@ep-xyz.aws.neon.tech/dbname?sslmode=require
   ```
5. Add to Vercel as `DATABASE_URL`

**Option B: Heroku Postgres**

1. Create Heroku app
2. Add "Heroku Postgres" addon (free tier)
3. Copy `DATABASE_URL` from Heroku config vars
4. Add to Vercel environment variables

**Option C: Railway**

1. Create Railway project
2. Add PostgreSQL service
3. Copy connection string
4. Add to Vercel

### 2.5 Deploy

1. Click **"Deploy"** in Vercel dashboard
2. Wait for build to complete (2-3 minutes)
3. Your API will be live at: `https://your-project.vercel.app`

### 2.6 Test Deployment

Open in browser:
- `https://your-project.vercel.app/` - Should show API info
- `https://your-project.vercel.app/docs` - FastAPI Swagger UI
- `https://your-project.vercel.app/health` - Health check
- `https://your-project.vercel.app/status` - Status with DB info

---

## 📱 STEP 3: Deploy Streamlit Frontend

### Why Separate Deployment?
Streamlit requires a persistent server process, which doesn't work on Vercel's serverless platform. Use Streamlit Cloud instead.

### 3.1 Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click **"New app"**
4. Select:
   - **Repository:** `datavineo/ElectraLens`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`

### 3.2 Configure Streamlit Secrets

In Streamlit Cloud dashboard, go to **App Settings → Secrets**

Add:

```toml
API_BASE = "https://your-vercel-app.vercel.app"
```

### 3.3 Update CORS in Vercel

After Streamlit is deployed, update `ALLOWED_ORIGINS` in Vercel:

```
ALLOWED_ORIGINS=https://your-app.streamlit.app,http://localhost:8501
```

---

## 🧪 STEP 4: Testing & Verification

### Local Testing Checklist:

```bash
# 1. Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy from .env.example)
cp .env.example .env

# 4. Edit .env with your DATABASE_URL

# 5. Test backend locally
python run_api.py
# Visit: http://localhost:8000/docs

# 6. Test frontend locally (in new terminal)
streamlit run streamlit_app.py
# Visit: http://localhost:8501
```

### Production Testing Checklist:

- [ ] Backend API responds: `https://your-app.vercel.app/`
- [ ] Swagger docs work: `https://your-app.vercel.app/docs`
- [ ] Health check passes: `https://your-app.vercel.app/health`
- [ ] Status shows database: `https://your-app.vercel.app/status`
- [ ] CORS allows Streamlit: Test from frontend
- [ ] Create voter endpoint works (POST `/voters`)
- [ ] List voters works (GET `/voters`)
- [ ] Search works (GET `/voters/search?q=test`)
- [ ] Authentication works (POST `/auth/login`)
- [ ] Streamlit app loads
- [ ] Streamlit can connect to API
- [ ] All dashboard features work

---

## 🔐 STEP 5: Security & Best Practices

### Environment Variables Security:

✅ **DO:**
- Use environment variables for all secrets
- Use PostgreSQL for production (not SQLite)
- Enable SSL/TLS for database connections
- Rotate database passwords regularly
- Use different DATABASE_URL for dev/staging/prod

❌ **DON'T:**
- Commit `.env` file to Git (already in `.gitignore`)
- Use SQLite in production (data loss on restart)
- Hardcode passwords or API keys
- Use same DB for dev and production

### CORS Configuration:

Current setting in `app/main.py`:
```python
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8501').split(',')
```

For production, set:
```
ALLOWED_ORIGINS=https://your-streamlit-app.streamlit.app
```

---

## 🐛 STEP 6: Troubleshooting

### Issue: Vercel Build Fails

**Error:** `ModuleNotFoundError: No module named 'slowapi'`

**Fix:** Add `slowapi==0.1.9` to `requirements.txt`

---

### Issue: Database Connection Error

**Error:** `could not connect to server`

**Fix:**
1. Verify `DATABASE_URL` in Vercel environment variables
2. Ensure PostgreSQL allows connections from Vercel IPs
3. Check SSL mode: `?sslmode=require`
4. Test connection string locally first

---

### Issue: CORS Error in Browser

**Error:** `Access to fetch at 'https://api.vercel.app' from origin 'https://streamlit.app' has been blocked by CORS policy`

**Fix:**
1. Update `ALLOWED_ORIGINS` in Vercel to include Streamlit URL
2. Redeploy Vercel app
3. Clear browser cache

---

### Issue: 500 Internal Server Error

**Fix:**
1. Check Vercel logs: Dashboard → Deployments → Select deployment → Logs
2. Look for Python exceptions
3. Verify all environment variables are set
4. Test endpoints locally first

---

### Issue: Streamlit Can't Connect to API

**Error:** `requests.exceptions.ConnectionError`

**Fix:**
1. Verify `API_BASE` in Streamlit secrets
2. Ensure URL has no trailing slash
3. Test API URL directly in browser
4. Check Vercel logs for rate limiting

---

## 📊 STEP 7: Monitoring & Maintenance

### Vercel Monitoring:

- **Logs:** Dashboard → Deployments → Select deployment → Logs
- **Analytics:** Dashboard → Analytics (requests, errors, performance)
- **Functions:** Monitor serverless function execution times

### Database Monitoring:

- **Neon:** Dashboard shows connection count, query performance
- **Heroku:** Use Heroku CLI: `heroku pg:info`
- **Railway:** Dashboard shows metrics

### Rate Limits:

Current limits in `app/main.py`:
- General endpoints: 100-200 req/min
- Upload PDF: 20 req/min
- Login: 10 req/min

Monitor in logs for `Rate limit exceeded` warnings.

---

## 🎯 Quick Command Reference

### Local Development:

```bash
# Start backend
uvicorn app.main:app --reload --port 8000

# Or use wrapper script
python run_api.py

# Start frontend
streamlit run streamlit_app.py

# Run tests (if you add them)
pytest tests/

# Check for errors
python -m pylint app/
```

### Vercel CLI (Optional):

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from terminal
vercel --prod

# View logs
vercel logs

# Check environment variables
vercel env ls
```

### Database Migration (if needed):

```bash
# Connect to production DB
psql $DATABASE_URL

# Create backup
pg_dump $DATABASE_URL > backup.sql

# Restore backup
psql $NEW_DATABASE_URL < backup.sql
```

---

## ✅ Final Deployment Checklist

Before going live:

- [ ] Fixed `app/database.py` to support PostgreSQL
- [ ] Created `requirements.txt` with all dependencies
- [ ] Set up production PostgreSQL database (Neon/Heroku/Railway)
- [ ] Created Vercel project and connected GitHub repo
- [ ] Set all environment variables in Vercel
- [ ] Deployed backend to Vercel successfully
- [ ] Tested backend API endpoints work
- [ ] Deployed frontend to Streamlit Cloud
- [ ] Updated `API_BASE` in Streamlit secrets
- [ ] Updated `ALLOWED_ORIGINS` in Vercel to include Streamlit URL
- [ ] Tested full app flow (login, create voter, search, etc.)
- [ ] Verified CORS is working
- [ ] Checked Vercel logs for errors
- [ ] Documented admin credentials securely
- [ ] Set up monitoring/alerts (optional)

---

## 📞 Support & Resources

### Documentation:
- **FastAPI:** https://fastapi.tiangolo.com/
- **Vercel:** https://vercel.com/docs
- **Streamlit:** https://docs.streamlit.io/
- **Neon DB:** https://neon.tech/docs/

### Your Project:
- **GitHub:** https://github.com/datavineo/ElectraLens
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Streamlit Cloud:** https://share.streamlit.io/

---

## 🎉 Next Steps After Deployment

1. **Create Admin User:**
   ```bash
   # Run locally or via API
   curl -X POST "https://your-app.vercel.app/auth/users" \
     -d "username=admin&password=secure_password&role=admin&full_name=Admin User"
   ```

2. **Import Initial Data:**
   - Use "Upload PDF" feature in Streamlit
   - Or bulk import via API

3. **Monitor Performance:**
   - Check Vercel analytics
   - Monitor database query times
   - Watch for rate limit hits

4. **Set Up Custom Domain (Optional):**
   - Vercel Dashboard → Domains
   - Add your domain
   - Update DNS records

5. **Enable Analytics (Optional):**
   - Add Vercel Analytics
   - Add Google Analytics to Streamlit

---

**Good luck with your deployment! 🚀**

If you encounter issues, check the troubleshooting section or review Vercel logs.

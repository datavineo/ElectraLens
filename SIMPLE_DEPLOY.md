# ElectraLens API - Simple Deployment Guide

## 🚀 Architecture (Simplified)

**Vercel Deployment**: 
- **Entry Point**: `api/index.py` → imports `app/main_vercel.py`
- **Runtime**: Uvicorn automatically handles the FastAPI app
- **Database**: SQLite for Vercel, PostgreSQL for local

## 📁 Key Files

```
api/
├── index.py          # Vercel entry point (imports main_vercel)
app/
├── main_vercel.py    # Clean FastAPI app (no heavy dependencies)
├── database.py       # Auto-detects Vercel vs local environment
vercel.json           # Simple build configuration
run_api.py           # Local development server
```

## 🔧 How It Works

### **Vercel Deployment**:
1. Vercel runs `api/index.py`
2. Sets `VERCEL=1` environment variable
3. Imports `app.main_vercel:app`
4. Uvicorn serves the FastAPI app
5. Database auto-switches to SQLite

### **Local Development**:
```bash
python run_api.py
```
- Uses PostgreSQL from `.env` file
- Hot reload enabled
- Runs on `http://localhost:8000`

## 📋 Environment Variables

### **Vercel Dashboard** (Set these):
```
DATABASE_URL=postgresql://your-neon-url...
ALLOWED_ORIGINS=https://your-frontend-domain.com
LOG_LEVEL=INFO
```

### **Local `.env`** (Already configured):
```
DATABASE_URL=postgresql://neondb_owner:npg_aTq54cvMEkiz@ep-orange-sea-ad3n3cx8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
ALLOWED_ORIGINS=http://localhost:8501
LOG_LEVEL=INFO
```

## 🎯 API Endpoints

After deployment:
- **Root**: `/` - API information
- **Docs**: `/docs` - Interactive API documentation
- **Health**: `/health` - Service status
- **Voters**: `/voters` - Full CRUD operations
- **Search**: `/voters/search/{name}` - Search by name
- **Stats**: `/stats` - Database statistics

## ✅ Benefits of This Approach

1. **Simple**: Direct uvicorn execution (no complex mounting)
2. **Reliable**: Standard FastAPI deployment pattern
3. **Clean**: Minimal dependencies in production
4. **Flexible**: Environment-aware database switching
5. **Debuggable**: Clear error messages and status endpoints

## 🚀 Deploy Now

1. **Push to GitHub** (already done)
2. **Import to Vercel** from your GitHub repo
3. **Set environment variables** in Vercel dashboard
4. **Deploy** - Should work immediately!

The API will be available at `https://your-app.vercel.app/`
# Vercel Environment Variables - Quick Reference

## Copy these to Vercel Dashboard
**Location:** Project Settings → Environment Variables

```bash
# Production PostgreSQL Database
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# Allowed CORS Origins (update after Streamlit deployment)
ALLOWED_ORIGINS=https://your-streamlit-app.streamlit.app,http://localhost:8501

# Logging Level
LOG_LEVEL=INFO
```

---

## Streamlit Cloud Secrets
**Location:** App Settings → Secrets

```toml
API_BASE = "https://your-vercel-app.vercel.app"
```

---

## Database Provider Examples

### Neon (Recommended - Free Tier)
```
postgresql://user:password@ep-xyz-123.aws.neon.tech/dbname?sslmode=require
```
**Sign up:** https://neon.tech/

### Railway
```
postgresql://postgres:password@containers-xyz.railway.app:5432/railway
```
**Sign up:** https://railway.app/

### Heroku Postgres
```
postgres://user:pass@ec2-xyz.compute-1.amazonaws.com:5432/dbname
```
**Note:** Heroku Postgres deprecated free tier (use Neon instead)

---

## Deployment URLs

After deployment, your app will be at:

- **Backend API:** `https://your-project.vercel.app`
- **API Docs:** `https://your-project.vercel.app/docs`
- **Frontend:** `https://your-app.streamlit.app`

---

## Quick Test Commands

```bash
# Test API health
curl https://your-project.vercel.app/health

# Test API status
curl https://your-project.vercel.app/status

# List voters
curl https://your-project.vercel.app/voters

# Test authentication
curl -X POST "https://your-project.vercel.app/auth/login?username=admin&password=yourpass"
```

---

## Environment-Specific Settings

| Environment | DATABASE_URL | ALLOWED_ORIGINS |
|-------------|--------------|-----------------|
| **Local Dev** | `sqlite:///./voters.db` | `http://localhost:8501` |
| **Vercel Preview** | PostgreSQL (same as prod or separate staging DB) | Preview Streamlit URL |
| **Production** | PostgreSQL (Neon/Railway) | Production Streamlit URL |

---

## Security Checklist

- [ ] Use PostgreSQL for production (NOT SQLite)
- [ ] Enable SSL for database (`?sslmode=require`)
- [ ] Use strong, unique passwords
- [ ] Never commit `.env` file to Git
- [ ] Rotate database credentials regularly
- [ ] Use different databases for dev/staging/prod
- [ ] Set up database backups

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'slowapi'"
**Fix:** Ensure `requirements.txt` includes `slowapi==0.1.9`

### Issue: "Database connection failed"
**Fix:** 
1. Verify `DATABASE_URL` format
2. Check database allows connections from Vercel
3. Ensure `?sslmode=require` is in connection string

### Issue: "CORS error" in browser console
**Fix:**
1. Update `ALLOWED_ORIGINS` in Vercel
2. Include your Streamlit URL
3. Redeploy Vercel app

### Issue: "502 Bad Gateway"
**Fix:**
1. Check Vercel function logs
2. Verify all dependencies in `requirements.txt`
3. Check database is accessible

---

## Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **Streamlit Docs:** https://docs.streamlit.io/
- **Neon Docs:** https://neon.tech/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

**For full deployment guide, see:** `VERCEL_DEPLOYMENT_GUIDE.md`

# ElectraLens - Vercel Deployment

## 🚀 Deploy on Vercel

This application is configured for deployment on Vercel with the following structure:

### Architecture
- **Backend**: FastAPI (deployed as Vercel Functions)
- **Frontend**: Streamlit (separate deployment)
- **Database**: SQLite (for demo) / PostgreSQL (for production)

### Deployment Steps

#### 1. Deploy Backend API on Vercel

1. **Connect Repository**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import from GitHub: `datavineo/ElectraLens`

2. **Configure Build Settings**:
   - Framework Preset: "Other"
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

3. **Environment Variables**:
   Set these in Vercel's Environment Variables section:
   - `DATABASE_URL`: Your PostgreSQL database URL
   - `ALLOWED_ORIGINS`: Your frontend URL
   - `LOG_LEVEL`: INFO

4. **Deploy**: Click "Deploy"

#### 2. Deploy Frontend on Streamlit Cloud

Since Streamlit needs a persistent server, deploy it separately:

1. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
2. **Connect GitHub**: Link your GitHub account
3. **Deploy App**:
   - Repository: `datavineo/ElectraLens`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

4. **Update API Base URL** in `streamlit_app.py`:
   ```python
   API_BASE = 'https://your-vercel-app.vercel.app/api'
   ```

#### 3. Alternative: Full Vercel Deployment

For a single deployment, you can use Vercel's Python support:

1. **Configure `vercel.json`** (already created)
2. **Push to GitHub**
3. **Deploy on Vercel**

### Configuration Files

- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Vercel-compatible API entry point
- ✅ `requirements.txt` - Python dependencies

### API Endpoints

Once deployed, your API will be available at:
- **Base URL**: `https://your-app.vercel.app/api`
- **Documentation**: `https://your-app.vercel.app/api/docs`
- **Health Check**: `https://your-app.vercel.app/health`

### Environment Configuration

#### Local Development
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your PostgreSQL database URL:
   ```
   DATABASE_URL="postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>?sslmode=require"
   ALLOWED_ORIGINS=http://localhost:8501
   LOG_LEVEL=INFO
   ```

#### Vercel Production
Set these environment variables in Vercel Dashboard:
- `DATABASE_URL`: Your PostgreSQL connection string
- `ALLOWED_ORIGINS`: Your frontend domain
- `LOG_LEVEL`: INFO

### Production Considerations

1. **Database**: PostgreSQL configured via environment variables
2. **Environment Variables**: Use .env for local, Vercel dashboard for production
3. **CORS**: Configure allowed origins for your frontend
4. **Rate Limiting**: Already configured with slowapi
5. **Logging**: Configure production logging

### Troubleshooting

- **Build Issues**: Check Python version compatibility
- **Import Errors**: Ensure all dependencies are in requirements.txt
- **Database Issues**: Use PostgreSQL for production (SQLite has limitations on Vercel)
- **CORS Issues**: Update ALLOWED_ORIGINS environment variable

### Support

Visit the [Vercel Documentation](https://vercel.com/docs) for more deployment options.
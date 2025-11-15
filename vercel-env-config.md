# =============================================================================
# ELECTRALENS VERCEL DEPLOYMENT CONFIGURATION
# =============================================================================
# Add these environment variables to your Vercel project settings

# 🔒 REQUIRED ENVIRONMENT VARIABLES FOR VERCEL
# =============================================================================

# PostgreSQL Database (Neon)
DATABASE_URL=postgresql://neondb_owner:npg_aTq54cvMEkiz@ep-orange-sea-ad3n3cx8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# JWT Secret Key (CHANGE THIS!)
JWT_SECRET_KEY=ElectraLens-Production-Secret-2024-CHANGE-THIS-IMMEDIATELY

# Application Environment
ENVIRONMENT=production
DEBUG=false

# Application URLs
FRONTEND_URL=https://datavineo.vercel.app
BACKEND_URL=https://electra-lens.vercel.app
API_BASE_URL=https://electra-lens.vercel.app

# CORS Configuration
CORS_ORIGINS=["https://datavineo.vercel.app","https://electra-lens.vercel.app","https://datavineo.github.io"]

# Default Credentials (CHANGE THESE IMMEDIATELY!)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=SecureAdmin2024!
DEFAULT_ADMIN_FULLNAME=System Administrator

DEFAULT_VIEWER_USERNAME=viewer
DEFAULT_VIEWER_PASSWORD=SecureViewer2024!
DEFAULT_VIEWER_FULLNAME=Demo Viewer

# Security Settings
RATE_LIMITING_ENABLED=true
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SESSION_TIMEOUT_MINUTES=30

# Database Connection Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

# =============================================================================
# HOW TO SET THESE IN VERCEL:
# =============================================================================

# Method 1: Using Vercel CLI
# vercel env add DATABASE_URL production
# vercel env add JWT_SECRET_KEY production
# ... (repeat for each variable)

# Method 2: Using Vercel Dashboard
# 1. Go to https://vercel.com/dashboard
# 2. Select your project: electra-lens
# 3. Go to Settings > Environment Variables
# 4. Add each variable above with the specified values
# 5. Set environment to: Production, Preview, Development (as needed)

# Method 3: Using vercel.json (for non-sensitive values only)
# Already configured in your vercel.json file

# =============================================================================
# PRODUCTION SECURITY CHECKLIST:
# =============================================================================

# ✅ Change JWT_SECRET_KEY to a strong random value
# ✅ Change DEFAULT_ADMIN_PASSWORD and DEFAULT_VIEWER_PASSWORD
# ✅ Verify DATABASE_URL points to production PostgreSQL
# ✅ Set DEBUG=false for production
# ✅ Configure proper CORS_ORIGINS (remove localhost for production)
# ✅ Enable RATE_LIMITING_ENABLED=true
# ✅ Set secure session timeouts
# ✅ Monitor logs for any security issues

# =============================================================================
# DEPLOYMENT VERIFICATION:
# =============================================================================

# After setting environment variables, verify:
# 1. https://electra-lens.vercel.app/health - Should show "healthy"
# 2. https://electra-lens.vercel.app/status - Should show production config
# 3. https://datavineo.vercel.app - Frontend should load and login should work
# 4. Test login with your updated credentials
# 5. Verify all CORS origins are working properly
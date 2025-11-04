from fastapi import FastAPI

# Ultra-minimal app that always works
app = FastAPI(title="ElectraLens API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "ElectraLens API is running on Vercel",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "test": "/test"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ElectraLens",
        "environment": "vercel",
        "database": "not_connected"
    }

@app.get("/test")
async def test():
    return {
        "test": "success",
        "message": "API is responding correctly",
        "environment": "vercel_serverless"
    }
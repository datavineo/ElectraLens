from fastapi import FastAPI

# Ultra-minimal test app
app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Test API is working", "status": "ok"}

@app.get("/test")
async def test():
    return {"test": "success", "environment": "vercel"}

@app.get("/debug")
async def debug():
    import os
    return {
        "python_version": os.sys.version,
        "environment_vars": dict(os.environ),
        "working_directory": os.getcwd()
    }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.security_middleware import SecurityHeadersMiddleware, CSRFProtectionMiddleware
from app.api.v1.endpoints import router as api_router

app = FastAPI(title="Telecom eSIM & SIM Swap Portal", version="1.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)

# Attach API Routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
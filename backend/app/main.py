from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import generate, jobs

app = FastAPI(title="Replace Lyrics API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])


@app.get("/")
async def root():
    return {"message": "Replace Lyrics API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

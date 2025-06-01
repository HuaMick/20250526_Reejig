"""
Main FastAPI application for O*NET Skills Gap API.
"""
import os
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "env", "env.env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="O*NET Skills Gap API",
    description="API for analyzing skill gaps between occupations using O*NET data",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import and include routers
from src.api.routers import skill_gap
from src.api.routers import db

app.include_router(skill_gap.router, prefix="/api/v1", tags=["skill-gap"])
#app.include_router(db.router, prefix="/api/v1", tags=["diagnostics"])

@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint for health check.
    """
    return {"status": "healthy", "message": "O*NET Skills Gap API is running"}

@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Use port from environment variable if available, otherwise default to 8000
    port = int(os.getenv("API_PORT", "8000"))
    # Use host from environment variable if available, otherwise default to 0.0.0.0
    host = os.getenv("API_HOST", "0.0.0.0")
    
    logger.info(f"Starting API server at {host}:{port}")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=True) 
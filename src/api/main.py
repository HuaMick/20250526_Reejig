"""
Main FastAPI application for O*NET Skills Gap API.
"""
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Header
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

# API Key Authentication
API_KEY_ENV = os.getenv("API_KEY")
if not API_KEY_ENV:
    logger.warning("Initial Check: API_KEY environment variable not found or empty after script load. Authentication checks will fail if enforced by routes.")
else:
    logger.info(f"Initial Check: API_KEY environment variable loaded: '{API_KEY_ENV[:4]}...'") # Log a portion for confirmation

async def verify_api_key(x_api_key: str = Header(None)):
    """
    Dependency to verify the API key.
    Expects API key in the 'X-API-Key' header.
    """
    logger.info("--- verify_api_key CALLED ---")
    logger.info(f"Value of API_KEY_ENV (server-side): '{API_KEY_ENV[:4]}...' if set, else None/Empty")
    logger.info(f"Value of x_api_key (from client header): {x_api_key}")

    if not API_KEY_ENV:
        logger.error("SERVER CONFIG ERROR: API_KEY environment variable is not set or empty. Authentication cannot be performed.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Server API key not configured.",
        )

    if not x_api_key:
        logger.warning("CLIENT ERROR: Request missing X-API-Key header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
        
    if x_api_key != API_KEY_ENV:
        # Avoid logging the actual received key in production if it's sensitive, 
        # but for debugging, knowing what was received can be useful.
        logger.warning(f"CLIENT ERROR: Invalid API Key received. Expected prefix: '{API_KEY_ENV[:4]}...', Received: '{x_api_key[:4]}...'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    logger.info("--- verify_api_key PASSED --- Client API key validated.")
    return x_api_key

# Import and include routers
from src.api.routers import skill_gap
from src.api.routers import db

app.include_router(skill_gap.router, prefix="/api/v1", tags=["skill-gap"], dependencies=[Depends(verify_api_key)])
#app.include_router(db.router, prefix="/api/v1", tags=["diagnostics"], dependencies=[Depends(verify_api_key)])

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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any

from .services.ai_visualizer import generate_visual_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="MindCanvas API",
    description="AI-powered abstract idea visualizer",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Pydantic models
class UserInput(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500, description="The abstract concept to visualize")

class VisualResponse(BaseModel):
    visual_description: str
    success: bool = True

class ErrorResponse(BaseModel):
    error: str
    success: bool = False

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MindCanvas API"}

# Main visualization endpoint
@app.post("/api/v1/visualize", response_model=VisualResponse)
async def visualize_concept(user_input: UserInput) -> Dict[str, Any]:
    """
    Generate a visual description for an abstract concept.
    
    Args:
        user_input (UserInput): Contains the prompt text to visualize
        
    Returns:
        VisualResponse: Contains the generated visual description
        
    Raises:
        HTTPException: If there's an error generating the description
    """
    try:
        logger.info(f"Received visualization request for: {user_input.prompt[:50]}...")
        
        # Generate visual description using the AI service
        visual_description = await generate_visual_description(user_input.prompt)
        
        logger.info("Visual description generated successfully")
        
        return VisualResponse(
            visual_description=visual_description,
            success=True
        )
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        logger.error(f"Error in visualize_concept: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate visual description. Please try again."
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to MindCanvas API",
        "description": "Transform abstract ideas into vivid visual descriptions",
        "endpoints": {
            "visualize": "/api/v1/visualize",
            "health": "/health"
        }
    }

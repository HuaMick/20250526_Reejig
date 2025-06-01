"""
Router for skill gap analysis endpoints.
"""
import logging, os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status

from src.functions.get_skills_gap import get_skills_gap
from src.functions.get_skills_gap_by_lvl import get_skills_gap_by_lvl
from src.config.api_exception_handles import handle_exception, handle_custom_error
from src.config.schemas import get_sqlalchemy_engine


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/skill-gap")
async def get_occupation_skill_gap(
    from_occupation: str = Query(..., description="Source occupation O*NET-SOC code (e.g., '11-1011.00')"),
    to_occupation: str = Query(..., description="Target occupation O*NET-SOC code (e.g., '11-2021.00')"),
):
    """
    Analyze the basic skill gap between two occupations.
    
    This endpoint compares two occupations and identifies skills that are present 
    in the target occupation but not in the source occupation.
    
    Args:
        from_occupation: O*NET-SOC code for the source occupation
        to_occupation: O*NET-SOC code for the target occupation
        
    Returns:
        JSON response with skill gap analysis:
        {
            "from_occupation": {
                "code": str,
                "title": str
            },
            "to_occupation": {
                "code": str,
                "title": str
            },
            "skill_gaps": [
                str (skill name)
            ]
        }
    """
    try:
        engine = get_sqlalchemy_engine(
            db_name=os.getenv("MYSQL_DATABASE"),
            db_user=os.getenv("MYSQL_USER"),
            db_password=os.getenv("MYSQL_PASSWORD"),
            db_host=os.getenv("MYSQL_HOST"),
            db_port=os.getenv("MYSQL_PORT")
        )
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error connecting to database: {e}")

    try:
        logger.info(f"Processing basic skill gap request: from={from_occupation}, to={to_occupation}")
        
        # Use the basic function without proficiency levels
        result = get_skills_gap(from_occupation, to_occupation, engine=engine)
        
        if not result["success"]:
            logger.error(f"Error in get_skills_gap: {result['message']}")
            # Use custom error handler for consistent error handling
            raise handle_custom_error(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"].lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=result["message"]
            )
        
        # Transform the internal result structure to match the API response format
        api_response = {
            "from_occupation": {
                "code": from_occupation,
                "title": result["result"]["from_occupation_title"]
            },
            "to_occupation": {
                "code": to_occupation,
                "title": result["result"]["to_occupation_title"]
            },
            "skill_gaps": result["result"]["skill_gaps"]  # List of skill names
        }
        
        logger.info(f"Successfully processed basic skill gap request. Found {len(api_response['skill_gaps'])} skill gaps.")
        return api_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Use the generic exception handler for unexpected errors
        logger.exception(f"Unexpected error processing skill gap request: {str(e)}")
        raise handle_exception(e)


@router.get("/skill-gap-by-lvl")
async def get_occupation_skill_gap_by_level(
    from_occupation: str = Query(..., description="Source occupation O*NET-SOC code (e.g., '11-1011.00')"),
    to_occupation: str = Query(..., description="Target occupation O*NET-SOC code (e.g., '11-2021.00')"),
):
    """
    Analyze the detailed skill gap between two occupations with proficiency levels.
    
    This endpoint compares two occupations and identifies skills that have higher 
    proficiency requirements in the target occupation compared to the source occupation.
    
    Args:
        from_occupation: O*NET-SOC code for the source occupation
        to_occupation: O*NET-SOC code for the target occupation
        
    Returns:
        JSON response with skill gap analysis:
        {
            "from_occupation": {
                "code": str,
                "title": str
            },
            "to_occupation": {
                "code": str,
                "title": str
            },
            "skill_gaps": [
                {
                    "skill_name": str,
                    "element_id": str,
                    "from_proficiency": float/int,
                    "to_proficiency": float/int
                }
            ]
        }
    """

    try:
        engine = get_sqlalchemy_engine(
            db_name=os.getenv("MYSQL_DATABASE"),
            db_user=os.getenv("MYSQL_USER"),
            db_password=os.getenv("MYSQL_PASSWORD"),
            db_host=os.getenv("MYSQL_HOST"),
            db_port=os.getenv("MYSQL_PORT")
        )
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error connecting to database: {e}")

    try:
        logger.info(f"Processing detailed skill gap request: from={from_occupation}, to={to_occupation}")
        
        # Use the enhanced function with proficiency levels
        result = get_skills_gap_by_lvl(from_occupation, to_occupation, engine=engine)
        
        if not result["success"]:
            logger.error(f"Error in get_skills_gap_by_lvl: {result['message']}")
            # Use custom error handler for consistent error handling
            raise handle_custom_error(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"].lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=result["message"]
            )
        
        # Transform the internal result structure to match the API response format
        api_response = {
            "from_occupation": {
                "code": from_occupation,
                "title": result["result"]["from_occupation_title"]
            },
            "to_occupation": {
                "code": to_occupation,
                "title": result["result"]["to_occupation_title"]
            },
            "skill_gaps": [
                {
                    "skill_name": gap["element_name"],
                    "element_id": gap["element_id"],
                    "from_proficiency": gap["from_data_value"],
                    "to_proficiency": gap["to_data_value"]
                }
                for gap in result["result"]["skill_gaps"]
            ]
        }
        
        logger.info(f"Successfully processed detailed skill gap request. Found {len(api_response['skill_gaps'])} skill gaps.")
        return api_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Use the generic exception handler for unexpected errors
        logger.exception(f"Unexpected error processing skill gap request: {str(e)}")
        raise handle_exception(e) 
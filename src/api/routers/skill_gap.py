"""
Router for skill gap analysis endpoints.
"""
import logging, os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status

from src.functions.get_skills_gap import get_skills_gap
from src.functions.get_skills_gap_by_lvl import get_skills_gap_by_lvl
from src.functions.get_skills_gap_by_lvl_llm import get_skills_gap_by_lvl_llm
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


@router.get("/skill-gap-llm")
async def get_occupation_skill_gap_llm(
    from_occupation: str = Query(..., description="Source occupation O*NET-SOC code (e.g., '11-1011.00')"),
    to_occupation: str = Query(..., description="Target occupation O*NET-SOC code (e.g., '11-2021.00')"),
):
    """
    Analyze the detailed skill gap between two occupations with LLM-generated descriptions.
    
    This endpoint compares two occupations and identifies skills that have higher 
    proficiency requirements in the target occupation compared to the source occupation,
    providing LLM-generated descriptions for each gap.
    
    Args:
        from_occupation: O*NET-SOC code for the source occupation
        to_occupation: O*NET-SOC code for the target occupation
        
    Returns:
        JSON response with LLM-enhanced skill gap analysis:
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
                    "to_proficiency": float/int,
                    "llm_gap_description": str
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
        logger.info(f"Processing LLM-enhanced skill gap request: from={from_occupation}, to={to_occupation}")
        
        result = get_skills_gap_by_lvl_llm(from_occupation, to_occupation, engine=engine)
        
        if not result["success"]:
            logger.error(f"Error in get_skills_gap_by_lvl_llm: {result['message']}")
            raise handle_custom_error(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"].lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=result["message"]
            )
        
        # The result["result"] from get_skills_gap_by_lvl_llm is already a list of skill gap dicts
        # We need to get the occupation titles from one of the earlier calls or from the message if available
        # For now, let's assume titles are part of the message or make a small helper if needed
        # This part might need refinement based on exact structure of successful message
        
        # Re-fetch basic occupation info for titles (can be optimized by get_skills_gap_by_lvl_llm returning them)
        from_title = "Unknown"
        to_title = "Unknown"
        try:
            # A bit inefficient, but ensures titles are present for the response
            # This could be optimized by having get_skills_gap_by_lvl_llm return titles
            from_details_res = get_skills_gap(from_occupation, to_occupation, engine) # or a get_occupation_details func
            if from_details_res["success"]:
                from_title = from_details_res["result"]["from_occupation_title"]
                to_title = from_details_res["result"]["to_occupation_title"]
        except Exception as title_e:
            logger.warning(f"Could not retrieve occupation titles for LLM gap response: {title_e}")

        api_response = {
            "from_occupation": {
                "code": from_occupation,
                "title": from_title 
            },
            "to_occupation": {
                "code": to_occupation,
                "title": to_title
            },
            "skill_gaps": result["result"] # This is already the list of gap objects
        }
        
        logger.info(f"Successfully processed LLM-enhanced skill gap request. Found {len(api_response['skill_gaps'])} skill gaps.")
        return api_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Use the generic exception handler for unexpected errors
        logger.exception(f"Unexpected error processing LLM skill gap request: {str(e)}")
        raise handle_exception(e) 
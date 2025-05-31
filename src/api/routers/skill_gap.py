"""
Router for skill gap analysis endpoints.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status

from src.functions.get_skills_gap import get_skills_gap
from src.functions.get_skills_gap_by_lvl import get_skills_gap_by_lvl

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/skill-gap")
async def get_occupation_skill_gap(
    from_occupation: str = Query(..., description="Source occupation O*NET-SOC code (e.g., '11-1011.00')"),
    to_occupation: str = Query(..., description="Target occupation O*NET-SOC code (e.g., '11-2021.00')"),
    include_proficiency: bool = Query(False, description="Include proficiency level details in the response")
):
    """
    Analyze the skill gap between two occupations.
    
    This endpoint compares two occupations and identifies skills that are:
    - Present in the target occupation but not in the source occupation
    - If include_proficiency=True: Also identifies skills with higher proficiency requirements in the target occupation
    
    Args:
        from_occupation: O*NET-SOC code for the source occupation
        to_occupation: O*NET-SOC code for the target occupation
        include_proficiency: Whether to include proficiency level details
        
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
                If include_proficiency=False:
                    str (skill name)
                    
                If include_proficiency=True:
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
        logger.info(f"Processing skill gap request: from={from_occupation}, to={to_occupation}, include_proficiency={include_proficiency}")
        
        if include_proficiency:
            # Use the enhanced function with proficiency levels
            result = get_skills_gap_by_lvl(from_occupation, to_occupation)
            
            if not result["success"]:
                logger.error(f"Error in get_skills_gap_by_lvl: {result['message']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"].lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
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
            
        else:
            # Use the basic function without proficiency levels
            result = get_skills_gap(from_occupation, to_occupation)
            
            if not result["success"]:
                logger.error(f"Error in get_skills_gap: {result['message']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"].lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
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
        
        logger.info(f"Successfully processed skill gap request. Found {len(api_response['skill_gaps'])} skill gaps.")
        return api_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a 500 response
        logger.exception(f"Unexpected error processing skill gap request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 
"""
This file contains the exception handles for the api.
It creates a dictionary of exception types and their corresponding error messages.
Other functions can then leverage this dictionary to handle the exception and return the appropriate error message.
The goal is to reduce the amount of code in the api functions and make them more readable.
"""
import logging
from typing import Dict, Type, Tuple, Any, Optional
from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

# Dictionary mapping exception types to (status_code, error_message) tuples
# This can be extended as needed for different types of exceptions
EXCEPTION_HANDLERS: Dict[Type[Exception], Tuple[int, str]] = {
    # Standard exceptions
    ValueError: (status.HTTP_400_BAD_REQUEST, "Invalid input value"),
    TypeError: (status.HTTP_400_BAD_REQUEST, "Invalid input type"),
    KeyError: (status.HTTP_400_BAD_REQUEST, "Required field missing"),
    
    # Custom exceptions for our application
    FileNotFoundError: (status.HTTP_404_NOT_FOUND, "Resource not found"),
    ConnectionError: (status.HTTP_503_SERVICE_UNAVAILABLE, "Service unavailable"),
    TimeoutError: (status.HTTP_504_GATEWAY_TIMEOUT, "Request timed out"),
    
    # Add more exception types as needed
}

def handle_exception(
    exception: Exception, 
    default_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    default_message: str = "An unexpected error occurred",
    log_error: bool = True,
    include_exception_detail: bool = True
) -> HTTPException:
    """
    Handle an exception and return an appropriate HTTPException.
    
    Args:
        exception: The exception to handle
        default_status_code: Default status code to use if exception type is not in EXCEPTION_HANDLERS
        default_message: Default message to use if exception type is not in EXCEPTION_HANDLERS
        log_error: Whether to log the error
        include_exception_detail: Whether to include exception details in the error message
        
    Returns:
        HTTPException: An HTTPException with appropriate status code and detail
    """
    # Get the exception class
    exception_class = exception.__class__
    
    # Look up status code and message for this exception type
    status_code, message = EXCEPTION_HANDLERS.get(
        exception_class, 
        (default_status_code, default_message)
    )
    
    # Add exception details if requested
    if include_exception_detail:
        detail = f"{message}: {str(exception)}"
    else:
        detail = message
    
    # Log the error if requested
    if log_error:
        logger.error(f"API Error ({status_code}): {detail}", exc_info=True)
    
    # Return an HTTPException
    return HTTPException(status_code=status_code, detail=detail)

def handle_custom_error(
    status_code: int, 
    message: str,
    exception: Optional[Exception] = None,
    log_error: bool = True
) -> HTTPException:
    """
    Create a custom HTTPException with the given status code and message.
    
    Args:
        status_code: HTTP status code
        message: Error message
        exception: Optional exception that caused this error
        log_error: Whether to log the error
        
    Returns:
        HTTPException: An HTTPException with the given status code and message
    """
    # Log the error if requested
    if log_error:
        if exception:
            logger.error(f"API Error ({status_code}): {message}", exc_info=exception)
        else:
            logger.error(f"API Error ({status_code}): {message}")
    
    # Return an HTTPException
    return HTTPException(status_code=status_code, detail=message)

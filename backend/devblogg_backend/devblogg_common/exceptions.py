import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Create a logger for this module
logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler cho DRF.
    """
    # Call handler default of DRF
    response = exception_handler(exc, context)

    # When DRF cant handle the exception
    if response is None:
        if isinstance(exc, Http404):
            data = {
                "success": False,
                "code": "not_found",
                "message": "Resource not found."
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(exc, PermissionDenied):
            data = {
                "success": False,
                "code": "permission_denied",
                "message": "You do not have permission to perform this action."
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

    
        logger.error(f"Unexpected error in {context['view'].__class__.__name__}: {exc}", exc_info=True)
        
        data = {
            "success": False,
            "code": "internal_server_error",
            "message": "An unexpected error occurred. Please contact support."
        }
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    if response is not None:
        custom_data = {
            "success": False,
            "code": "validation_error" if response.status_code == 400 else "error",
            "message": "Validation failed" if response.status_code == 400 else str(exc),
            "errors": response.data  
        }
        response.data = custom_data

    return response
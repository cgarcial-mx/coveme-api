from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from pydantic import ValidationError
import json
import logging

logger = logging.getLogger(__name__)


class PydanticValidationMiddleware(MiddlewareMixin):
    """
    Middleware to handle Pydantic validation errors and convert them to proper HTTP responses
    """
    
    def process_exception(self, request, exception):
        """
        Handle Pydantic validation errors
        """
        if isinstance(exception, ValidationError):
            # Convert Pydantic validation error to JSON response
            error_details = []
            
            for error in exception.errors():
                error_detail = {
                    'field': '.'.join(str(loc) for loc in error['loc']),
                    'message': error['msg'],
                    'type': error['type']
                }
                error_details.append(error_detail)
            
            response_data = {
                'error': 'Validation failed',
                'message': 'The provided data does not meet the required schema',
                'details': error_details,
                'status_code': 400
            }
            
            logger.warning(f"Pydantic validation error for {request.path}: {error_details}")
            
            return JsonResponse(
                response_data,
                status=400,
                content_type='application/json'
            )
        
        # Let other exceptions be handled by Django's default error handling
        return None


class PydanticRequestMiddleware(MiddlewareMixin):
    """
    Middleware to validate incoming request data with Pydantic schemas
    """
    
    def process_request(self, request):
        """
        Process incoming requests and validate JSON data if present
        """
        # Only process requests with JSON content
        if request.content_type == 'application/json' and request.body:
            try:
                # Parse JSON body
                json_data = json.loads(request.body)
                request.pydantic_data = json_data
            except json.JSONDecodeError as e:
                return JsonResponse(
                    {
                        'error': 'Invalid JSON',
                        'message': 'The request body contains invalid JSON',
                        'details': str(e),
                        'status_code': 400
                    },
                    status=400,
                    content_type='application/json'
                )
        
        return None


def validate_request_data(schema_class):
    """
    Decorator to validate request data with a Pydantic schema
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if hasattr(request, 'pydantic_data'):
                try:
                    # Validate data with Pydantic schema
                    validated_data = schema_class(**request.pydantic_data)
                    request.validated_data = validated_data
                except ValidationError as e:
                    error_details = []
                    for error in e.errors():
                        error_detail = {
                            'field': '.'.join(str(loc) for loc in error['loc']),
                            'message': error['msg'],
                            'type': error['type']
                        }
                        error_details.append(error_detail)
                    
                    return JsonResponse(
                        {
                            'error': 'Request validation failed',
                            'message': 'The request data does not meet the required schema',
                            'details': error_details,
                            'status_code': 400
                        },
                        status=400,
                        content_type='application/json'
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

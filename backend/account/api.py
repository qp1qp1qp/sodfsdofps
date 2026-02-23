from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging
import secrets

logger = logging.getLogger(__name__)

# This should be a secure, randomly generated key stored in your environment variables
API_KEY = settings.API_KEY

@api_view(['POST'])
def get_api_key(request):
    if request.data.get('secret') == settings.API_SECRET:
        return Response({
            'api_key': settings.API_KEY
        })
    return Response({
        'error': 'Invalid secret'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def secure_endpoint(request):
    api_key = request.headers.get('X-API-Key')
    if api_key and api_key == API_KEY:
        # Your secure data or functionality here
        return Response({
            'status': 'success',
            'message': 'This is a secure endpoint'
        })
    return Response({
        'status': 'error',
        'message': 'Invalid API key'
    }, status=status.HTTP_401_UNAUTHORIZED)
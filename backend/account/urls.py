from django.urls import path
from . import api

urlpatterns = [
    path('get-api-key/', api.get_api_key, name='get_api_key'),
    # Remove the following lines as they're no longer needed
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('signup/', api.signup, name='signup'),
]

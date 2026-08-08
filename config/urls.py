from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

urlpatterns = [
    path('api-lotomania/', include('api.urls')),
    path('api-lotomania/admin/', admin.site.urls),
    path('api-lotomania/token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api-lotomania/token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('api-lotomania/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api-lotomania/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api-lotomania/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
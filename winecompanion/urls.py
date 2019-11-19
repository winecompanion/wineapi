"""winecompanion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from users.token import MyTokenObtainPairView
from api.views import GenderView, LanguageView
from users.views import WineUserView

schema_view = get_swagger_view(title='WineCompanion APIs')

router = routers.DefaultRouter()
router.register(r'users', WineUserView, basename='users')
router.register(r'languages', LanguageView, basename='languages')
router.register(r'genders', GenderView, basename='genders')

urlpatterns = [
    path(r'swagger-docs/', schema_view),
    path('api/', include('api.urls')),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('admin/', include('smuggler.urls')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

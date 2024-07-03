from django.urls import path, include
from rest_framework import routers

from .views import TitleViewSet

router = routers.DefaultRouter()

router.register(
    'titles', TitleViewSet, basename='titles'
)

urlpatterns = [
    path('', include(router.urls))
]

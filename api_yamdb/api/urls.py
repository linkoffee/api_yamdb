from django.urls import path, include
from rest_framework import routers

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = routers.DefaultRouter()

router.register(
    'titles', TitleViewSet, basename='titles'
)
router.register(
    'genres', GenreViewSet, basename='genres'
)
router.register(
    'categories', CategoryViewSet, basename='categories'
)


urlpatterns = [
    path('', include(router.urls))
]

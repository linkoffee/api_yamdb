from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (APISignup, CategoryViewSet, GenreViewSet,
                    MyTokenObtainView, MyUserViewSet, TitleViewSet)

router = DefaultRouter()
router.register(
    'titles', TitleViewSet, basename='titles'
)
router.register(
    'genres', GenreViewSet, basename='genres'
)
router.register(
    'categories', CategoryViewSet, basename='categories'
)


user_router = SimpleRouter()
user_router.register(
    'users',
    MyUserViewSet,
    basename='users'
)
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(user_router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path(
        'v1/auth/token/',
        MyTokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
]

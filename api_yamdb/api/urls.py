from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import MyUserViewSet


v1_router = SimpleRouter()
v1_router.register(
    r'users/(?P<username>\[a-zA-Z0-9]+)/$',
    MyUserViewSet,
    basename='UserModel',
)


urlpatterns = [
    path('v1/', include('djoser.urls.authtoken')),
    path('v1/users/<slug>', include(v1_router.urls)),
    path('v1/auth/signup/',
         MyUserViewSet.as_view({'post': 'create'}), name="register"),
    path(
        'v1/auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),  # последних двух нет в ТЗ
    path(
        'v1/auth/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),  # но они нужны/желательны
    path('v1/', include('djoser.urls')),
    # path('v1/', include(v1_router.urls)),
]


"""
Для обновления access-токена не нужно применять refresh-токен и 
дополнительный эндпоинт. Токен обновляется через повторную передачу 
username и кода подтверждения.
"""

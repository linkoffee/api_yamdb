from .views import MyUserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.routers import SimpleRouter
from djoser.views import UserViewSet
from django.urls import include, path
from .views import CategoryViewSet, GenreViewSet, TitleViewSet
from rest_framework import routers
from django.urls import path, include
<< << << < HEAD


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
== == == =


v1_router = SimpleRouter()
v1_router.register(
    r'users/(?P<username>\[a-zA-Z0-9]+)/$',
    MyUserViewSet,
    basename='UserModel',
)


urlpatterns = [
    path('', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
    path('auth/signup/',
         MyUserViewSet.as_view({'post': 'create'}), name="register"),
    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),  # последних двух нет в ТЗ
    path(
        'auth/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),  # но они нужны/желательны
    path('', include('djoser.urls')),
    # path('v1/', include(v1_router.urls)),
]


"""
Для обновления access-токена не нужно применять refresh-токен и 
дополнительный эндпоинт. Токен обновляется через повторную передачу 
username и кода подтверждения.
"""
>>>>>> > feature / users

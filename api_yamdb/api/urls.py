from .views import MyUserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.routers import SimpleRouter, DefaultRouter
from djoser.views import UserViewSet
from django.urls import include, path


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
    r'users/(?P<username>\[a-zA-Z0-9]+)/$',
    MyUserViewSet,
    basename='UserModel',
)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls.authtoken')),
    path('v1/', include(user_router.urls)),
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
    # path('v1/', include(user_router.urls)),
]

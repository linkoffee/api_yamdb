from .views import MyUserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.routers import SimpleRouter, DefaultRouter
from djoser.views import UserViewSet
from django.urls import include, path, re_path


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


urlpatterns = [    # некоторые урлы в двух местах, пока не уверен, какие должны находиться первыми
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls.authtoken')),
    path('v1/', include('djoser.urls')),
    re_path(
        # [\w.@+-]+\Z  в тз, [a-zA-Z0-9]+)/$ , [a-z0-9]+(?:-[a-z0-9]+)*$
        r'^v1/users/(?P<username>[\w.@+-]+)/$',
        MyUserViewSet.as_view({'get': 'retrieve'}),
    ),
    # path('v1/', include(user_router.urls)),
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
    # path('v1/', include('djoser.urls')),
    # path('v1/', include(user_router.urls)),
]

from .views import MyUserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet, APISignup
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
    'users',
    MyUserViewSet,
    basename='users'
)
# user_router.register(r'users/(?P<username>\[\w.@+-]+)/$',MyUserViewSet,basename='UserModel',)
# re_path(r'^v1/users/(?P<username>[\w.@+-]+)/$',MyUserViewSet.as_view({'get': 'retrieve'})),

# [\w.@+-]+\Z  в тз, [a-zA-Z0-9]+)/$ , [a-z0-9]+(?:-[a-z0-9]+)*$
urlpatterns = [    # некоторые урлы в двух местах, пока не уверен, какие должны находиться первыми
    path('v1/', include(router.urls)),
    # path('v1/', include('djoser.urls.authtoken')),
    # path('v1/', include('djoser.urls.base')),
    path('v1/', include(user_router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path(
        'v1/auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    # path('v1/', include('djoser.urls')),
    # path('v1/', include(user_router.urls)),
]

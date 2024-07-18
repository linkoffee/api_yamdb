from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    APITokenObtainView, APIUserViewSet, ReviewViewSet,
                    APISignup, TitleViewSet)

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
router.register(
    r'^titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router.register('users', APIUserViewSet, basename='users')

authurl = [
    path('signup/',
         APISignup.as_view(), name='signup'),
    path(
        'token/',
        APITokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(authurl)),
]

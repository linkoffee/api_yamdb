from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    MyTokenObtainView, MyUserViewSet, ReviewViewSet,
                    SignupViewSet, TitleViewSet)

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
router.register('users', MyUserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/',  # Выносим одинаковые префиксы в отдельный список.
         SignupViewSet.as_view({'post': 'post'}), name='signup'),
    path(
        'v1/auth/token/',
        MyTokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
]

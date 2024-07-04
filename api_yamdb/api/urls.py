from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

# from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet


"""v1_router = SimpleRouter() 
v1_router.register('posts', PostViewSet) 
v1_router.register('groups', GroupViewSet) 
v1_router.register( 
    r'posts/(?P<post_id>\d+)/comments', 
    CommentViewSet, 
    basename='CommentModel', 
) 
v1_router.register('follow', FollowViewSet, basename='FollowModel') """


urlpatterns = [
    # path('v1/', include('djoser.urls.jwt')),
    # path('v1/auth/', include('djoser.urls.jwt')), здесь должен быть /signup/
    path(
        'v1/auth/token',
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
    )  # но они нужны/желательны
    # path('v1/', include(v1_router.urls)),
]


"""
Для обновления access-токена не нужно применять refresh-токен и 
дополнительный эндпоинт. Токен обновляется через повторную передачу 
username и кода подтверждения.
"""

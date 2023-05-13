from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APIGetTokenView, APISignUpView,
                    ReviewViewSet, UsersViewSet,
                    CategoryViewSet, GenreViewSet, TitleViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('title', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/token/', APIGetTokenView.as_view(), name='token'),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', APISignUpView.as_view(), name='signup')
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APIGetTokenView, APISignUpView,
                    ReviewViewSet, UsersViewSet,
                    CategoryViewSet, GenreViewSet, TitleViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('title', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

urlpatterns = [
    path('v1/auth/token/', APIGetTokenView.as_view(), name='token'),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignUpView.as_view(), name='signup')
]

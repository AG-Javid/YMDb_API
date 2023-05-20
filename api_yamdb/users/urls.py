from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import APIGetTokenView, APISignUpView, UsersViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', APIGetTokenView.as_view()),
    path('v1/auth/signup/', APISignUpView.as_view())
]

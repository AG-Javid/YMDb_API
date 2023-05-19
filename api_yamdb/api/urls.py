from django.urls import include, path

from api.v1.urls import urlpatterns as v1

urlpatterns = [
    path('v1/', include(v1))
]

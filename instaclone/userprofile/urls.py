from rest_framework import routers
from .views import ProfileViewSet
from django.urls import path, include, re_path
from rest_framework.authtoken import views


router = routers.SimpleRouter()
router.register(r'api/profiles', ProfileViewSet, 'profiles')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('api/profiles/login', views.obtain_auth_token)
]

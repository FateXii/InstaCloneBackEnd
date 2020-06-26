from rest_framework import routers
from .views import ProfileViewSet
from django.urls import path, include, re_path


router = routers.SimpleRouter()
router.register(r'profiles', ProfileViewSet, 'profiles')

urlpatterns = [
    path('', include(router.urls)),
]

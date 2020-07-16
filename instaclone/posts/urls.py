from rest_framework import routers
from .views import PostViewSet
from django.urls import path, include, re_path


router = routers.SimpleRouter()
router.register(r'posts', PostViewSet, 'posts')

urlpatterns = [
    path('', include(router.urls)),
]

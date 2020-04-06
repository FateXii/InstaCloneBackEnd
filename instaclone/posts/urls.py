from rest_framework import routers
from .views import PostViewSet
from comments.views import CommentViewSet
from django.urls import path, include, re_path


router = routers.SimpleRouter()
router.register(r'api/posts', PostViewSet, 'posts')

urlpatterns = [
    path('', include(router.urls)),
]

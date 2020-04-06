from rest_framework import routers
from .views import CommentViewSet
from django.urls import path

router = routers.SimpleRouter()
router.register('api/comments', CommentViewSet, 'comments')

urlpatterns = router.urls

from .models import Post
from .serializers import PostSerializer
from rest_framework import viewsets, permissions


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = PostSerializer

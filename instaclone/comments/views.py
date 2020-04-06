from .models import Comment
from .serializers import CommentSerializer
from rest_framework import viewsets, permissions


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = CommentSerializer

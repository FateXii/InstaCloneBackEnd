from django.shortcuts import render
from .models import Post
from .serializers import PostSerializer
from rest_framework import viewsets
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view
        requires.
        """
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def create(self, request):
        request_data = request.data
        request_data['profile'] = request.user.profile.id
        serializer = self.serializer_class(
            data=request_data,
            context={'context', request}
        )
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.data
            serializer.create(validated_data)
        return Response(
            validated_data,
            status=status.HTTP_201_CREATED)

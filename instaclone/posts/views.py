from django.shortcuts import render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .permissions import IsUserWhoPosted, PosterIsNotPrivateOrUserIsFollowing
from .serializers import PostSerializer


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = "pk_uuid"

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view
    #     requires.
    #     """
    #     if self.action in ['create', 'destroy']:
    #         permission_classes = [
    #             permissions.IsAuthenticated,
    #             IsUserWhoPosted
    #         ]
    #     elif self.action in ['list', 'detail']:
    #         permission_classes = [
    #             IsUserWhoPosted,
    #             PosterIsNotPrivateOrUserIsFollowing
    #         ]

    #     else:
    #         permission_classes = []

    #     return [permission() for permission in permission_classes]

    # def create(self, request):
    #     request_data = request.data
    #     request_data['profile'] = request.user.profile.id
    #     serializer = self.serializer_class(
    #         data=request_data,
    #         context={'context', request}
    #     )
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_201_CREATED
    #     )

from .models import Profile
from .serializers import ProfileSerializer
from rest_framework import viewsets, permissions


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = ProfileSerializer

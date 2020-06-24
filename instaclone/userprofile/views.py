from .models import Profile
from .serializers import ProfileSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    serializer_class = ProfileSerializer

    @action(detail=True, methods=['post'] permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        user = self.request.user
        to_follow = Profile.objects.get(pk)
        if not to_follow.is_private:
            to_follow.followed_by_set.add(user)
            user.follow_set.add(to_follow)
        else:
            to_follow.follow_requests_set.add(user)

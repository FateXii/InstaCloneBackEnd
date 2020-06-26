from .models import Profile
from .serializers import ProfileSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework import status


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(
        detail=True, methods=['post'],
        permission_classes=[permissions.IsAuthenticated])
    def follow(self, request,  pk):
        current_profile = self.request.user.profile
        profile_to_follow = Profile.objects.get(pk=pk)

        if current_profile.id == profile_to_follow.id:
            return Response(
                data={
                    'error': 'Cannot follow self'
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        if not profile_to_follow.is_private:
            profile_to_follow.followed_by.add(current_profile)
            current_profile.following.add(profile_to_follow)
            return Response(
                data={'status': 'Following @{}.'.format(
                    profile_to_follow.user.username)},
                status=status.HTTP_200_OK
            )

        profile_to_follow.follow_requests_received.add(current_profile)
        current_profile.follow_requests_submitted.add(profile_to_follow)
        return Response(
            data={'status': 'request to follow @{} submitted.'.format(
                profile_to_follow.user.username)},
            status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['post'],
        permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request,  pk):
        current_profile = self.request.user.profile
        profile_to_unfollow = Profile.objects.get(pk=pk)

        if current_profile.following.get(pk=pk):
            profile_to_unfollow.followed_by.remove(current_profile)
            current_profile.following.remove(profile_to_unfollow)
            return Response(
                data={'status': 'Unfollowed @{}.'.format(
                    profile_to_unfollow.user.username)},
                status=status.HTTP_200_OK)
        return Response(
            data={'error': 'Not following @{}'.format(
                current_profile.following.get(pk=pk).user.username)},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    @action(
        detail=True, methods=['post'],
        permission_classes=[permissions.IsAuthenticated])
    def accept_follow_request(self, request,  pk):
        current_profile = self.request.user.profile
        profile_requesting_follow = Profile.objects.get(pk=pk)

        current_profile.followed_by.add(profile_requesting_follow)
        profile_requesting_follow.following.add(current_profile)

        current_profile.follow_requests_received.remove(
            profile_requesting_follow)
        profile_requesting_follow.follow_requests_submitted.remove(
            current_profile)
        return Response(
            data={'status': 'Follow request by @{} accepted.'.format(
                profile_requesting_follow.user.username)},
            status=status.HTTP_200_OK)

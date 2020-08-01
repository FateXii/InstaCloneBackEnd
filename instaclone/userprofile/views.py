from .models import Profile
from .serializers import ProfileSerializer, LoginSerializer
import userprofile.permissions as custom_permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view,\
    permission_classes,\
    renderer_classes
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.contrib.auth.models import User as DjangoUser


# from .permissions import IsCurrentUser
# from posts.serializers import PostSerializer
# from rest_framework import status


@ api_view(['POST'])
# @renderer_classes([BrowsableAPIRenderer])
def login(request):
    serializer = LoginSerializer(
        data=request.data,
        context={'request', request}
    )
    serializer.is_valid(raise_exception=True)
    profile = serializer.validated_data['profile']
    token, created = Token.objects.get_or_create(user=profile.user)
    profile.user.last_login = timezone.now()
    profile.user.save()
    return Response(status=status.HTTP_200_OK, data={
        'token': token.key,
        'profile': ProfileSerializer(profile).data,
        'logged_in': True,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
# @renderer_classes([BrowsableAPIRenderer])
def logout(request):
    user = DjangoUser.objects.get(id=request.user.id)
    user.auth_token.delete()
    if user.auth_token.key:
        return Response(status=420, data={})
    return Response(status=status.HTTP_200_OK, data={
        'token': None,
        'profile': None,
        'logged_in': False,
    })


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'pk_uuid'

def get_permissions(self):
    """
    Instantiates and returns the list of permissions that this view
    requires.
    """
        if self.action in [
                       'partial_update',
            'update',
                       ]:
            permission_classes = [
                permissions.IsAuthenticated,
                custom_permissions.IsCurrentUser

            ]
    else:
        permission_classes = []

    return [permission() for permission in permission_classes]


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
        current_profile.following.add(profile_to_follow)
        return Response(
            data={'status': 'Following @{}.'.format(
                profile_to_follow.user.username)},
            status=status.HTTP_200_OK
        )

    profile_to_follow.follow_requests_received.add(current_profile)
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

    if current_profile.following.filter(id=pk).count():
        current_profile.following.remove(profile_to_unfollow)
        return Response(
            data={'status': 'Unfollowed @{}.'.format(
                profile_to_unfollow.user.username)},
            status=status.HTTP_200_OK)
    return Response(
        data={'error': 'Not following user'},
        status=status.HTTP_406_NOT_ACCEPTABLE
    )


@action(
    detail=True, methods=['post'],
    permission_classes=[permissions.IsAuthenticated])
def accept_follow_request(self, request,  pk):
    current_profile = self.request.user.profile
    profile_requesting_follow = Profile.objects.get(pk=pk)

    if current_profile.follow_requests_received.filter(id=pk):

        profile_requesting_follow.following.add(current_profile)

        current_profile.follow_requests_received.remove(
            profile_requesting_follow)
        return Response(
            data={'status': 'Follow request by @{} accepted.'.format(
                profile_requesting_follow.user.username)},
            status=status.HTTP_200_OK)
    return Response(
        data={
            'error': 'Follow request not found'
        },
        status=status.HTTP_406_NOT_ACCEPTABLE)


@action(
    detail=True,
    methods=['post'],
    permission_classes=[permissions.IsAuthenticated]
)
def reject_follow_request(self, request,  pk):
    current_profile = self.request.user.profile
    profile_requesting_follow = Profile.objects.get(pk=pk)

    if current_profile.follow_requests_received.filter(id=pk):
        current_profile.follow_requests_received.remove(
            profile_requesting_follow)
        return Response(
            data={'status': 'Follow request by @{} rejected.'.format(
                profile_requesting_follow.user.username)},
            status=status.HTTP_200_OK)

    return Response(
        data={
            'error': 'Follow request not found'
        },
        status=status.HTTP_406_NOT_ACCEPTABLE)


@action(
    detail=True,
    methods=['get']
)
def get_posts(self, request, pk):
    current_profile = self.request.user.profile

    is_authenticated = self.request.user.is_authenticated
    requested_profile = Profile.objects.get(pk=pk)
    is_following = bool(
        requested_profile.following.filter(
            id=current_profile.id).count())
    is_current_user = (int(pk) == current_profile.id) and is_authenticated

    if is_current_user or (requested_profile.is_private and is_following):
        raw_posts = requested_profile.posts.all()
        posts = PostSerializer(raw_posts, many=True).data
        return Response(
            data={'posts': posts},
            status=status.HTTP_200_OK)
    else:
        return Response(
            data={'error': 'profile is private'},
            status=status.HTTP_200_OK)

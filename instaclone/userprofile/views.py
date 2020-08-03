from .models import Profile, FollowRequests
from .serializers import ProfileSerializer,\
    LoginSerializer,\
    BaseProfileSerializer
from rest_framework.response import Response
from rest_framework.decorators import action, api_view,\
    permission_classes,\
    renderer_classes
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser, User as DjangoUser
from django.shortcuts import get_object_or_404, get_list_or_404
import userprofile.permissions as custom_permissions


@ api_view(['POST'])
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
def logout(request):
    user = get_object_or_404(DjangoUser, id=request.user.id)
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
            'destroy',
            'follow',
        ]:
            permission_classes = [
                custom_permissions.IsAuthenticatedCurrentUserObj

            ]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    @action(
        detail=True,
        methods=['post'],
        url_name='follow'
    )
    def follow(self, request,  pk_uuid):
        current_profile = request.user.profile
        profile_to_follow = get_object_or_404(
            self.get_queryset(),
            pk_uuid=pk_uuid
        )
        already_requested = profile_to_follow in [
            _request.request_to for _request in
            current_profile.requests_sent.all()
        ]
        already_following = profile_to_follow in current_profile.following.all()
        if profile_to_follow != current_profile and not already_following and\
                not already_requested:
            message = {}
            if not profile_to_follow.is_private:
                current_profile.following.add(profile_to_follow)
                message['code'] = 'follow'
                message['message'] = '{}'.format(profile_to_follow.pk_uuid)
            else:
                message['code'] = 'request'
                follow_request = FollowRequests.objects.create(
                    request_from=current_profile,
                    request_to=profile_to_follow
                )
                message['message'] = '{}'.format(follow_request.pk_uuid)
            return Response(
                data=message,
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                'code': 'follow',
                'message': 'forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    @action(
        detail=True,
        methods=['post'],
        url_name='unfollow'
    )
    def unfollow(self, request,  pk_uuid):
        current_profile = request.user.profile
        profile_to_unfollow = get_object_or_404(
            self.get_queryset(),
            pk_uuid=pk_uuid
        )
        if profile_to_unfollow in current_profile.following.all():
            current_profile.following.remove(profile_to_unfollow)
            return Response(
                data={},
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                'code': 'unfollow',
                'message': 'forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['GET'])
@permission_classes(
    [
        custom_permissions.IsAuthenticatedCurrentUserView,
    ]
)
def requests_sent_view(request,  pk_uuid):
    serializer = BaseProfileSerializer
    profile = get_object_or_404(Profile, pk_uuid=pk_uuid)
    request_sent_by_profile = profile.requests_sent.all()
    profiles_sent_to = [
        request_sent.request_to for request_sent in request_sent_by_profile
    ]
    profiles = serializer(profiles_sent_to, many=True)
    return Response(
        data=profiles.data,
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes(
    [
        custom_permissions.IsAuthenticatedCurrentUserView
    ]
)
def requests_received_view(request,  pk_uuid):
    serializer = BaseProfileSerializer
    profile = get_object_or_404(Profile, pk_uuid=pk_uuid)
    requests_received_by_profile = profile.requests_received.all()
    profiles_from = [
        _request.request_from for
        _request in requests_received_by_profile
    ]
    profiles = serializer(profiles_from, many=True)
    return Response(
        data=profiles.data,
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes(
    [
        custom_permissions.IsAuthenticatedCurrentUserView
    ]
)
def requests_detail_view(request,  pk_uuid, request_uuid):
    serializer = BaseProfileSerializer
    profile = get_object_or_404(Profile, pk_uuid=pk_uuid)
    _request = get_object_or_404(FollowRequests, pk_uuid=request_uuid)
    if _request.request_to == profile:
        request_from = get_object_or_404(
            Profile, pk_uuid=_request.request_from.pk_uuid)
        data = {
            'pk_uuid': _request.pk_uuid,
            'request_from': serializer(request_from).data,
            'request_to': serializer(profile).data,
            'accepted': _request.accepted
        }
        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )
    return Response(
        data={},
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(['POST'])
@permission_classes(
    [
        custom_permissions.IsAuthenticatedCurrentUserView
    ]
)
def requests_accept_view(request,  pk_uuid, request_uuid):
    serializer = BaseProfileSerializer
    profile = get_object_or_404(Profile, pk_uuid=pk_uuid)
    _request = get_object_or_404(FollowRequests, pk_uuid=request_uuid)
    if _request.request_to == profile:
        if _request.rejected is None:
            request_from = get_object_or_404(
                Profile, pk_uuid=_request.request_from.pk_uuid)
            _request.accepted = timezone.now()
            request_from.following.add(profile)
            _request.save()
            return Response(
                data={},
                status=status.HTTP_200_OK,
            )
    return Response(
        data={},
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(['POST'])
@permission_classes(
    [
        custom_permissions.IsAuthenticatedCurrentUserView
    ]
)
def requests_reject_view(request,  pk_uuid, request_uuid):
    serializer = BaseProfileSerializer
    profile = get_object_or_404(Profile, pk_uuid=pk_uuid)
    _request = get_object_or_404(FollowRequests, pk_uuid=request_uuid)
    if _request.request_to == profile:
        if _request.accepted is None:
            request_from = get_object_or_404(
                Profile, pk_uuid=_request.request_from.pk_uuid)
            _request.rejected = timezone.now()
            _request.save()
            return Response(
                data={},
                status=status.HTTP_200_OK,
            )
    return Response(
        data={},
        status=status.HTTP_403_FORBIDDEN,
    )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from userprofile.serializers import LoginSerializer, BaseProfileSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    token = None
    return Response(status=status.HTTP_200_OK, data={
        'token': None,
        'profile': None,
        'logged_in': False,
    })


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(
        data=request.data, context={'request', request})
    serializer.is_valid(raise_exception=True)
    profile = serializer.validated_data['profile']
    token, created = Token.objects.get_or_create(user=profile.user.id)
    return Response(status=status.HTTP_200_OK, data={
        'token': token.key,
        'profile': BaseProfileSerializer(profile).data,
        'logged_in': True,
    })

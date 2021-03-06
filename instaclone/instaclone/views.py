# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import api_view,\
#     permission_classes,\
#     renderer_classes
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.renderers import BrowsableAPIRenderer
# from userprofile.serializers import LoginSerializer, BaseProfileSerializer
# from django.utils import timezone
# import pytz


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @renderer_classes([BrowsableAPIRenderer])
# def logout(request):
#     user = User.objects.get(id=request.user.id)
#     user.auth_token.delete()
#     if user.auth_token.key:
#         return Response(status=420, data={})
#     return Response(status=status.HTTP_200_OK, data={
#         'token': None,
#         'profile': None,
#         'logged_in': False,
#     })


# @ api_view(['POST'])
# @renderer_classes([BrowsableAPIRenderer])
# def login(request):
#     serializer = LoginSerializer(
#         data=request.data,
#         context={'request', request}
#     )
#     serializer.is_valid(raise_exception=True)
#     profile = serializer.validated_data['profile']
#     token, created = Token.objects.get_or_create(user=profile.user)
#     profile.user.last_login = timezone.now()
#     profile.user.save()
#     return Response(status=status.HTTP_200_OK, data={
#         'token': token.key,
#         'profile': BaseProfileSerializer(profile).data,
#         'logged_in': True,
#     })

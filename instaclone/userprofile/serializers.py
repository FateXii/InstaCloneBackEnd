from rest_framework import serializers
from django.contrib.auth import authenticate
# from comments.serializers import CommentSerializer
from django.contrib.auth.models import User
from django_countries.serializer_fields import CountryField
from .models import Profile, FollowRequests
from rest_framework.exceptions import ValidationError, ErrorDetail
import collections
import copy

# TODO: Serializer for redacted profiles


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type:password', })

    def validate(self, values):
        username = values.get('username')
        password = values.get('password')
        message = None

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                message = "Incorrect credentials"
        else:
            message = "Please provide login credentials"

        if message:
            raise serializers.ValidationError(message, code='authentication')

        values['profile'] = user.profile
        return values


class BaseProfileSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField()
    user = UserSerializer(write_only=True)
    username = serializers.CharField(
        # source specifies the name of the attribute
        # used to populate the field
        # user.username is used to flatten the data for
        # username, since the foreign
        # key relation would be an unnecessary indirection on the front end.
        source='user.username'
    )
    password = serializers.CharField(
        source='user.password',
        required=True,
        write_only=True,
        style={
            'input-type:password'
        }
    )
    email = serializers.EmailField(
        source='user.email'
    )
    first_name = serializers.CharField(
        source='user.first_name',
        required=False,
    )

    last_name = serializers.CharField(
        source='user.last_name',
        required=False
    )

    class Meta:
        model = Profile
        fields = ['pk_uuid', 'user', 'username', 'email', 'password',
                  'first_name', 'last_name', 'bio', 'is_private',
                  'phone_number',
                  ]
        read_only = ['pk_uuid']
        extra_kwargs = {
            'user': {'write_only': True},
            'password': {'write_only': True}
        }
        depth = 1

    def get_username(self, profile):
        return profile.user.username

    def get_email(self, profile):
        return profile.user.email

    def get_first_name(self, profile):
        return profile.user.first_name

    def get_last_name(self, profile):
        return profile.user.last_name

    def create(self, validated_data):
        user_data = {}
        password = ''
        for key, value in validated_data.pop('user').items():
            user_data[key] = value

        user = User.objects.create_user(
            username=user_data.pop('username'),
            email=user_data.pop('email'),
            password=user_data.pop('password'),
            **user_data
        )
        profile = Profile.objects.create(
            user=user,  **validated_data)
        return profile

    def validate(self, attrs):
        """
            Since profile is has a nested user User as to be validated first
        """
        user = attrs.pop('user', None)
        user_instance = self.instance.user if self.instance else None
        profile_keys = self.get_fields().keys()
        profile = {
            key: value for key, value in attrs.items()
            if key in profile_keys
        }
        for key in profile_keys:
            attrs.pop(key, None)
        if user:
            serialized_user = UserSerializer(
                instance=user_instance,
                data=user,
                partial=self.partial,
                **attrs)
            serialized_user.is_valid(raise_exception=True)
            attrs = {
                'user': dict(serialized_user.validated_data),
            }
        attrs = {
            **profile,
            **attrs,
        }
        return super().validate(attrs)

    def update(self, instance, validated_data):
        validated_user_data = validated_data.get('user', {})

        # Update user data
        instance.user.username = validated_user_data.get(
            'username', instance.user.username
        )
        instance.user.email = validated_user_data.get(
            'email', instance.user.email
        )
        instance.user.first_name = validated_user_data.get(
            'first_name', instance.user.first_name
        )
        instance.user.last_name = validated_user_data.get(
            'last_name', instance.user.last_name
        )
        instance.user.save()

        # Update profile data
        instance.bio = validated_data.get(
            'bio', instance.bio
        )
        instance.is_private = validated_data.get(
            'is_private', instance.is_private
        )
        instance.save()
        return instance


class ProfileSerializer(BaseProfileSerializer):
    following = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)

    followers = serializers.SerializerMethodField()

    follow_requests_received = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)

    follow_requests_sent = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['id', 'pk_uuid',  'username', 'email', 'password',
                  'first_name', 'last_name', 'bio', 'is_private',
                  'following', 'followers', 'follow_requests_received',
                  'follow_requests_sent', 'phone_number',
                  ]
        read_only = ['pk_uuid']
        extra_kwargs = {
            'user': {'write_only': True},
            'password': {'write_only': True}
        }
        depth = 1

    def get_followers(self, current_profile):
        profiles = Profile.objects.filter(
            following__pk_uuid=current_profile.pk_uuid)

        serialized_followers = BaseProfileSerializer(
            profiles,
            many=True, read_only=True,
            required=False, allow_null=True).data

        return serialized_followers

    def get_follow_requests_sent(self, current_profile):
        requests = FollowRequests.objects.filter(
            requests_sent__id=current_profile.id)

        serialized_follow_request = BaseProfileSerializer(
            requests,
            many=True, read_only=True,
            required=False, allow_null=True).data

        return serialized_follow_request

    def get_follow_requests_received(self, current_profile):
        requests = FollowRequests.objects.filter(
            requests_received__id=current_profile.id)

        serialized_follow_request = BaseProfileSerializer(
            requests,
            many=True, read_only=True,
            required=False, allow_null=True).data

        return serialized_follow_request

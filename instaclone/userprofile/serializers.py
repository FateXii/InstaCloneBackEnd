from rest_framework import serializers
from .models import Profile, PhoneNumber
# from comments.serializers import CommentSerializer
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'password']
        read_only = ['id']
        extra_kwargs = {'password': {'write_only': True}}


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['country_code', 'number']


class BaseProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField(
        allow_null=True, required=False)
    last_name = serializers.SerializerMethodField(
        allow_null=True, required=False)

    phone_number = PhoneNumberSerializer(allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'email',
                  'first_name', 'last_name', 'phone_number']

    def get_username(self, profile):
        return profile.user.username

    def get_first_name(self, profile):
        return profile.user.first_name

    def get_last_name(self, profile):
        return profile.user.last_name

    def get_email(self, profile):
        return profile.user.email


class ProfileSerializer(BaseProfileSerializer):
    user = UserSerializer(required=True, write_only=True)

    following = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)
    followed_by = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)
    follow_requests_received = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)
    follow_requests_submitted = BaseProfileSerializer(
        many=True, read_only=True,
        required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'email',
                  'first_name', 'last_name', 'bio', 'is_private',
                  'following', 'followed_by',
                  'phone_number',
                  'follow_requests_received',
                  'follow_requests_submitted']
        extra_kwargs = {'user': {'write_only': True}}
        depth = 1

    def create(self, validated_data):

        user_data = validated_data.pop('user')
        phone = None

        if 'phone_number'in validated_data.keys():
            phone_data = validated_data.pop('phone_number')
            phone = PhoneNumber.objects.create(**phone_data)

        user = User(
            email=user_data['email'],
            username=user_data['username']
        )
        user.set_password(user_data['password'])
        user.save()

        profile = Profile.objects.create(
            user=user, phone_number=phone, **validated_data)
        return profile

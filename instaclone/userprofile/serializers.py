from rest_framework import serializers
from .models import Profile, PhoneNumber
# from comments.serializers import CommentSerializer
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['country_code', 'number']


class SubProfile(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    phone_number = PhoneNumberSerializer(allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'is_private', 'phone_number']
        depth = 1


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    phone_number = PhoneNumberSerializer(allow_null=True, required=False)
    following = SubProfile(many=True, read_only=True,
                           required=False, allow_null=True)
    followed_by = SubProfile(many=True, read_only=True,
                             required=False, allow_null=True)
    follow_requests_received = SubProfile(many=True, read_only=True,
                                          required=False, allow_null=True)
    follow_requests_submitted = SubProfile(many=True, read_only=True,
                                           required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'is_private',
                  'following', 'followed_by',
                  'phone_number',
                  'follow_requests_received',
                  'follow_requests_submitted']
        depth = 1

    def create(self, validated_data):

        user_data = validated_data.pop('user')
        phone = None

        if 'phone_number'in validated_data.keys():
            phone_data = validated_data.pop('phone_number')
            phone = PhoneNumber.objects.create(**phone_data)

        user = user = User(
            email=user_data['email'],
            username=user_data['username']
        )
        user.set_password(user_data['password'])
        user.save()

        profile = Profile.objects.create(
            user=user, phone_number=phone, **validated_data)
        return profile

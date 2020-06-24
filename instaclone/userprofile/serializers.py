from rest_framework import serializers
from .models import Profile, PhoneNumber
# from comments.serializers import CommentSerializer
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    # phone_number = NumberSerializer(required=False)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'phone_number']
        depth = 2

    def create(self, validated_data):

        user_data = **validated_data.pop('user')
        user = User.objects.create(user_data)
        phone_data = **validated_data.pop('phone_number')

        profile = Profile.objects.create(user=user, **validated_data)

        phone = PhoneNumber.objects.create(profile=profile, phone_data)
        return profile


class NumberSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = PhoneNumber
        fields = ['profile', 'country_code', 'number']

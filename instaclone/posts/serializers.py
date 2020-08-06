from rest_framework import serializers
from .models import Post
from userprofile.models import Profile
from userprofile.serializers import BaseProfileSerializer


class PostSerializer(serializers.ModelSerializer):
    profile = BaseProfileSerializer()

    class Meta:
        model = Post
        fields = ['pk_uuid', 'profile', 'image', 'likes', 'shared']

    def create(self, validated_data):
        profile = Profile.objects.get(id=validated_data.pop('profile').id)
        post = Post.objects.create(
            profile=profile,
            **validated_data
        )
        return post

from rest_framework import serializers
from .models import Post
from userprofile.models import Profile


class PostSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all())

    class Meta:
        model = Post
        fields = ['profile', 'image', 'likes', 'shared']

    def create(self, validated_data):
        profile = Profile.objects.get(id=validated_data.pop('profile'))
        post = Post.objects.create(
            profile=profile,
            **validated_data
        )
        return post

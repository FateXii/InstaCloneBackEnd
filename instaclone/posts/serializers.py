from rest_framework import serializers
from .models import Post
# from comments.serializers import CommentSerializer


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

from rest_framework import serializers
from .models import Comment
# from post.serializers import PostSerializer


class CommentSerializer(serializers.ModelSerializer):

    replies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def validate(self, data):
        """
        Check that start is before finish.
        """
        errors = {}
        if data['isReply']:
            if 'post' in data.keys():
                errors['post-error'] = \
                    "cannot reply to post only a comment"
                raise serializers.ValidationError(errors)
            elif 'reply_to' not in data.keys():
                errors['reply_to-error'] = \
                    "replies require comment to reply to"
                raise serializers.ValidationError(errors)
        return data

from django.db import models
from posts.models import Post
from userprofile.models import Profile


class Comment(models.Model):
    user = models.ForeignKey(Profile,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             null=True)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    isReply = models.BooleanField(null=True, default=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments', null=True)
    reply_to = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='replies',
        null=True)

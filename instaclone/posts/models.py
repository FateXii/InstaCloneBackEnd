from django.db import models
from userprofile.models import Profile


class Post(models.Model):
    user = models.ForeignKey(Profile,
                             on_delete=models.CASCADE, related_name='posts')
    post_picture = models.URLField()
    caption = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

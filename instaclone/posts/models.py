from django.db import models
from userprofile.models import Profile

# Create your models here.


class Post(models.Model):
    profile = models.ForeignKey(
        Profile, models.CASCADE, related_name="posts")

    image = models.URLField()
    # created = models.DateTimeField(auto_now_add=True)
    # updated = models.DateTimeField(null=True, blank=True)
    likes = models.ForeignKey(
        Profile,
        models.CASCADE,
        related_name="likes",
        null=True,
        blank=True
    )
    shared = models.ForeignKey(
        Profile,
        models.CASCADE,
        related_name="shares",
        null=True,
        blank=True
    )

import uuid

from django.db import models
from django.utils import timezone

from userprofile.models import Profile

# Create your models here.


class Post(models.Model):
    pk_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    profile = models.ForeignKey(Profile, models.CASCADE, related_name="posts")

    image = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=255, null=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    likes = models.ForeignKey(
        Profile, models.CASCADE,
        related_name="likes",
        null=True,
        blank=True
    )

from django.db import models
from userprofile.models import Profile
from django.utils import timezone
import pytz
import uuid


class InstacloneBase(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)

# Create your models here.


class Post(models.Model):
    profile = models.ForeignKey(
        Profile, models.CASCADE, related_name="posts")

    image = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(
        max_length=255, null=True, blank=True)

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

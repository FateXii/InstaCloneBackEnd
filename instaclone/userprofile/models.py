from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)
    following = models.ForeignKey('self')
    followed_by = models.ForeignKey('self')
    follow_requests = models.ForeignKey('self')


class PhoneNumber(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=10)
    number = models.CharField(max_length=30)

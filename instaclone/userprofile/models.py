from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user_name = models.CharField(
        max_length=20, unique=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.URLField()
    phone_number = models.CharField(max_length=20, unique=True, null=True)

    def __str__(self):
        return user_name

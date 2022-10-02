from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user')
    role = models.CharField(max_length=10, default='student')

    def __str__(self):
        return self.user.username

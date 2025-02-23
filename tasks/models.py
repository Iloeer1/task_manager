from django.db import models
from django.contrib.auth.models import User

# Task is an instance with three fields: title, description, and user.
# Each task is associated with one user
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

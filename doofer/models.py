from django.contrib.auth.models import AbstractUser
from django.db import models
    

class Note(models.Model):
    title = models.CharField(max_length=255)
    comment = models.TextField()
    snippet = models.TextField()
    url = models.URLField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_updated_at = models.DateTimeField(auto_now=True)
    related = models.ManyToManyField('self', symmetrical=True)
    # the author - this should be a foreignKey to the User model but it caused errors
    user = models.IntegerField(default=0)
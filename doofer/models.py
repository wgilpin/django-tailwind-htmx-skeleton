from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add your custom fields here
    # For example:
    display_name = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users',
    )
    
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
    # user = models.ForeignKey(User, on_delete=models.CASCADE)

from typing import Collection
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from markdown import markdown # markdown -> html
from markdownify import markdownify  # html -> markdown
    


class Note(models.Model):
    URL_MAX_LENGTH = 2000

    title = models.CharField(blank=True, max_length=255)
    comment = models.TextField(blank=True)
    url = models.URLField(blank=True, max_length=URL_MAX_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_updated_at = models.DateTimeField(auto_now=True)
    related = models.ManyToManyField('self', symmetrical=True)
    # the author - this should be a foreignKey to the User model but it caused errors
    user = models.IntegerField(default=0)

    # validate model and convert html to markdown
    def clean(self) -> None:
        # truncate url to URL_MAX_LENGTH
        if self.url and len(self.url) > self.URL_MAX_LENGTH:
            self.url = self.url[:self.URL_MAX_LENGTH]

        # need at least one of title, comment, url
        if not any([self.title, self.comment, self.url]):
            raise ValidationError('Need at least one of title, comment, url')
        
        # convert any html to markdown
        if self.comment:
            self.comment = markdownify(self.comment)

    # convert markdown to html for display
    def as_html(self):
        return markdown(self.comment)
    
    # convert to string
    def __str__(self):
        return self.title
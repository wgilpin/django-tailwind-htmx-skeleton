from typing import Collection
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from markdown import markdown # markdown -> html
from markdownify import markdownify  # html -> markdown
    

class Note(models.Model):
    title = models.CharField(blank=True, max_length=255)
    comment = models.TextField(blank=True)
    snippet = models.TextField(blank=True)
    url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_updated_at = models.DateTimeField(auto_now=True)
    related = models.ManyToManyField('self', symmetrical=True)
    # the author - this should be a foreignKey to the User model but it caused errors
    user = models.IntegerField(default=0)

    # validate model and convert html to markdown
    def clean(self) -> None:
        # need at least one of title, comment, snippet, url
        if not any([self.title, self.comment, self.snippet, self.url]):
            raise ValidationError('Need at least one of title, comment, snippet, url')
        # convert html snippet to markdown
        if self.snippet:
            self.snippet = markdownify(self.snippet)

    # convert markdown to html for display
    def as_html(self):
        return markdown(self.snippet)
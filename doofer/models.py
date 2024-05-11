from django.db import models
from django.forms import ValidationError
from urllib.parse import urlparse, parse_qs
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
        """ truncate url to URL_MAX_LENGTH """
        if self.url and len(self.url) > self.URL_MAX_LENGTH:
            self.url = self.url[:self.URL_MAX_LENGTH]

        # need at least one of title, comment, url
        if not any([self.title, self.comment, self.url]):
            raise ValidationError('Need at least one of title, comment, url')

        # convert any html to markdown
        if self.comment:
            self.comment = markdownify(self.comment)

    def get_yt_thumbnail_url(self):
        """ get the video id from a the url if it's a youtube url """
        if 'youtube.com' in self.url:
            parsed_url = urlparse(self.url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v')
            if video_id:
                return f'https://img.youtube.com/vi/{video_id[0]}/sddefault.jpg'
        return None

    def __str__(self):
        """ convert to string """
        return str(self.title)

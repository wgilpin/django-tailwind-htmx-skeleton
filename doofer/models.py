from urllib.parse import parse_qs, urlparse

from django.db import models
from django.forms import ValidationError
from markdown import markdown
from markdownify import markdownify  # type: ignore[import-untyped]


class Note(models.Model):
    """Django model for a note object"""

    URL_MAX_LENGTH = 2000

    id: models.AutoField = models.AutoField(primary_key=True)
    title: models.CharField = models.CharField(blank=True, max_length=255)
    comment: models.TextField = models.TextField(blank=True)
    url: models.URLField = models.URLField(blank=True, max_length=URL_MAX_LENGTH)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    related_updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    related: models.ManyToManyField = models.ManyToManyField("self", symmetrical=True)
    # the author - this should be a foreignKey to the User model but it caused errors
    user: models.IntegerField = models.IntegerField(default=0)
    # the embeddings vector, to be replaced with pgvector later
    title_embedding: models.TextField = models.TextField(blank=True)
    content_embedding: models.TextField = models.TextField(blank=True)

    def get_title_embeddings(self) -> list[float]:
        """get the title embeddings as a list of floats"""
        return [float(e) for e in self.title_embedding.split(",") if e]

    def set_title_embeddings(self, embeddings: list[float]) -> None:
        """set the title embeddings as a list of floats"""
        self.title_embedding = ",".join([str(e) for e in embeddings])

    def set_content_embeddings(self, embeddings: list[float]) -> None:
        """set the content embeddings as a list of floats"""
        self.content_embedding = ",".join([str(e) for e in embeddings])

    def get_content_embeddings(self) -> list[float]:
        """get the content embeddings as a list of floats"""
        return [float(e) for e in self.content_embedding.split(",") if e]

    # validate model and convert html to markdown
    def clean(self) -> None:
        """truncate url to URL_MAX_LENGTH"""
        if self.url and len(self.url) > self.URL_MAX_LENGTH:
            self.url = self.url[: self.URL_MAX_LENGTH]

        # need at least one of title, comment, url
        if not any([self.title, self.comment, self.url]):
            raise ValidationError("Need at least one of title, comment, url")

        # convert any html to markdown
        if self.comment:
            self.comment = markdownify(self.comment)

    def content_as_html(self):
        """convert comment to html"""
        return markdown(self.comment)

    def get_yt_thumbnail_url(self):
        """get the video id from a the url if it's a youtube url"""
        if "youtube.com" in self.url:
            parsed_url = urlparse(self.url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get("v")
            if video_id:
                return f"https://img.youtube.com/vi/{video_id[0]}/sddefault.jpg"
        return None

    def __str__(self):
        """convert to string"""
        return str(self.title)

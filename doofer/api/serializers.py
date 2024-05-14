from rest_framework import serializers

from doofer.models import Note


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for the Note model"""

    class Meta:
        model = Note
        fields = ["id", "title", "comment", "url", "related"]
        read_only_fields = ("user", "related")
        extra_kwargs = {"user": {"read_only": True}}

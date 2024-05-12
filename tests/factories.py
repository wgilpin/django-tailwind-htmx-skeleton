import factory  # type: ignore[import-untyped]

from django.contrib.auth.models import User
from doofer.models import Note


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    is_superuser = False
    is_staff = False

    title_embedding = ""
    comment_embedding = ""


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Faker("sentence", nb_words=4)
    comment = factory.Faker("sentence", nb_words=10)
    url = factory.Faker("url")

    @factory.lazy_attribute
    def user(self, user_instance):
        return user_instance.id


def create_note_for_user(instance):
    return NoteFactory.create(user=instance.id)

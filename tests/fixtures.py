import pytest
from django.contrib.auth.models import User

from factories import create_note_for_user


@pytest.fixture()
def user_1(db):
    return User.objects.create(username="user_1")


@pytest.fixture()
def note_1(db, user_1):
    return create_note_for_user(user_1)


@pytest.fixture()
def note_2(db, user_1):
    return create_note_for_user(user_1)


@pytest.fixture()
def note_3(db, user_1):
    return create_note_for_user(user_1)

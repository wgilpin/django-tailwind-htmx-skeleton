import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from doofer.api.views import get_notes, note_create, note_detail
from doofer.models import Note

from fixtures import user_1, note_1, note_2


def test_get_notes(user_1, note_1, note_2):
    factory = APIRequestFactory()
    request = factory.get(f"/api/notes/")
    force_authenticate(request, user=user_1)

    response = get_notes(request)  # Pass pk argument for detail view

    assert response.status_code == status.HTTP_200_OK
    ids = [n.get("id") for n in response.data]
    assert note_1.id in ids
    assert note_2.id in ids


def test_get_note_detail(note_1, user_1):
    request = APIRequestFactory().get(f"/api/notes/{note_1.id}/")
    force_authenticate(request, user=user_1)

    response = note_detail(request, id_=note_1.id)  # Pass pk argument for detail view
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == note_1.title


@pytest.mark.django_db
def test_create_note(user_1):
    data = {"title": "Test Note 3", "comment": "This is a new test note."}
    request = APIRequestFactory().post("/api/notes/", data=data)
    force_authenticate(request, user=user_1)
    response = note_create(request)  # Pass pk argument for detail view
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Test Note 3"


def test_update_note(user_1, note_1):
    data = {"title": "Updated Note", "comment": "This is an updated test note."}
    request = APIRequestFactory().put(f"/api/notes/{note_1.id}/", data=data)

    response = note_detail(request, id_=note_1.id)  # Pass pk argument for detail view
    assert response.status_code == status.HTTP_403_FORBIDDEN

    force_authenticate(request, user=user_1)
    response = note_detail(request, id_=note_1.id)  # Pass pk argument for detail view
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]


def test_delete_note(user_1):
    note = Note.objects.create(
        user=user_1.id, title="Test Note 1", comment="This is a test note."
    )
    request = APIRequestFactory().delete(f"/api/notes/{note.id}/")

    # call the api unauthorized user
    response = note_detail(request, id_=note.id)  # Pass pk argument for detail view
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # now call the api with authorized user
    force_authenticate(request, user=user_1)
    response = note_detail(request, id_=note.id)  # Pass pk argument for detail view

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(Note.DoesNotExist) as exc_info:
        Note.objects.get(id=note.id)
    assert str(exc_info.value) == "Note matching query does not exist."

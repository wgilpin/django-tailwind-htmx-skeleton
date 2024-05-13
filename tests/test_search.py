import pytest

from doofer.embeddings import get_text_embedding
from doofer.models import Note
from doofer.search import (
    get_my_notes,
    get_similar_to_text,
    get_note_by_id,
    vecs_similar_ranked,
    do_text_search,
    do_note_search,
    get_embeddings_for_notes,
)
from fixtures import user_1, note_1, note_2, note_3


@pytest.mark.django_db
def test_getMyNotes(user_1, note_1):
    expected = list(Note.objects.filter(user=user_1.id))
    assert get_my_notes(user_1.id) == expected


@pytest.mark.django_db
def test_getSimilarToText(note_1, note_2, note_3):
    text = "search query"
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    count = 10
    expected = vecs_similar_ranked([get_text_embedding(text)], notes, "", count)
    assert get_similar_to_text(text, notes, count) == expected


@pytest.mark.django_db
def test_get_note_by_id(note_1, note_2, note_3):
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    id = "2"
    expected = Note.objects.get(id=id)
    assert get_note_by_id(notes, id) == expected


@pytest.mark.django_db
def test_vecsSimilarRanked(note_1, note_2, note_3):
    vecs = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    originalId = ""
    count = 10
    threshold = 0.25
    expected = vecs_similar_ranked(vecs, notes, originalId, count, threshold)
    assert vecs_similar_ranked(vecs, notes, originalId, count, threshold) == expected


@pytest.mark.django_db
def test_doTextSearch():
    searchText = "search query"
    maxResults = 10
    uid = "123"
    expected = do_text_search(searchText, maxResults, uid)
    assert do_text_search(searchText, maxResults, uid) == expected


@pytest.mark.django_db
def test_doNoteSearch(note_1):
    noteId = "1"
    maxResults = 10
    uid = "123"
    threshold = 0.25
    expected = do_note_search(noteId, maxResults, uid, threshold)
    assert do_note_search(noteId, maxResults, uid, threshold) == expected


@pytest.mark.django_db
def test_getEmbeddingsForNotes(note_1, note_2, note_3):
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    originalId = ""
    expected = get_embeddings_for_notes(notes, originalId)
    assert get_embeddings_for_notes(notes, originalId) == expected

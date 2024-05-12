import pytest

from doofer.embeddings import getTextEmbedding
from doofer.models import Note
from doofer.search import (
    noteSummariesToIds,
    getMyNotes,
    getSimilarToText,
    get_note_by_id,
    vecsSimilarRanked,
    doTextSearch,
    doNoteSearch,
    getEmbeddingsForNotes,
)
from fixtures import user_1, note_1, note_2, note_3


@pytest.mark.django_db
def test_noteSummariesToIds():
    summaries = [["1", "Title 1"], ["2", "Title 2"], ["3", "Title 3"]]
    expected = [
        {"id": "1", "title": "Title 1"},
        {"id": "2", "title": "Title 2"},
        {"id": "3", "title": "Title 3"},
    ]
    assert noteSummariesToIds(summaries) == expected


@pytest.mark.django_db
def test_getMyNotes(user_1, note_1):
    expected = list(Note.objects.filter(user=user_1.id))
    assert getMyNotes(user_1.id) == expected


@pytest.mark.django_db
def test_getSimilarToText(note_1, note_2, note_3):
    text = "search query"
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    count = 10
    expected = vecsSimilarRanked([getTextEmbedding(text)], notes, "", count)
    assert getSimilarToText(text, notes, count) == expected


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
    expected = vecsSimilarRanked(vecs, notes, originalId, count, threshold)
    assert vecsSimilarRanked(vecs, notes, originalId, count, threshold) == expected


@pytest.mark.django_db
def test_doTextSearch():
    searchText = "search query"
    maxResults = 10
    uid = "123"
    expected = doTextSearch(searchText, maxResults, uid)
    assert doTextSearch(searchText, maxResults, uid) == expected


@pytest.mark.django_db
def test_doNoteSearch(note_1):
    noteId = "1"
    maxResults = 10
    uid = "123"
    threshold = 0.25
    expected = doNoteSearch(noteId, maxResults, uid, threshold)
    assert doNoteSearch(noteId, maxResults, uid, threshold) == expected


@pytest.mark.django_db
def test_getEmbeddingsForNotes(note_1, note_2, note_3):
    notes = [
        Note.objects.get(id="1"),
        Note.objects.get(id="2"),
        Note.objects.get(id="3"),
    ]
    originalId = ""
    expected = getEmbeddingsForNotes(notes, originalId)
    assert getEmbeddingsForNotes(notes, originalId) == expected

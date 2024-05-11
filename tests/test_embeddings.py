import pytest

from doofer.models import Note
from doofer.embeddings import (
    cosine_similarity,
    getHFembeddings,
    getTextEmbedding,
    updateNoteEmbeddings,
    getNoteSimilarity,
)

def test_cosine_similarity():
    vector1 = [1, 2, 3]
    vector2 = [4, 5, 6]
    assert round(cosine_similarity(vector1, vector2), 2) == 0.97

def test_getHFembeddings():
    text = "This is a test."
    embeddings = getHFembeddings(text)
    assert len(embeddings) == 768

def test_getTextEmbedding():
    text = "This is a test."
    embeddings = getTextEmbedding(text)
    assert len(embeddings) == 768

def test_updateNoteEmbeddings():
    note = Note(title="This is a test.", comment="This is a test comment.")
    updated_note = updateNoteEmbeddings(note)
    assert updated_note.title_embedding is not None
    assert updated_note.content_embedding is not None

def test_getNoteSimilarity():
    note1 = Note(title="This is a test.", comment="This is a test comment.")
    note2 = Note(title="This is a different test.", comment="This is a different test comment.")
    similarity = getNoteSimilarity(note1, note2)
    assert similarity > 0.0

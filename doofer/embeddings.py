""" Routines for processing embeddings """

import math

from doofer.hf_model import get_hf_embeddings
from doofer.models import Note

EMBEDDINGS_SIZE = 384


def get_text_embedding(text: str) -> list[float]:
    """Get the embeddings for a given text"""
    try:
        vector: list[float] = get_hf_embeddings(text)
        return vector
    except Exception as error:
        print("HF API  error", {error})
        return []


def update_note_embeddings(note: Note) -> Note:
    """get the note embeddings from the db or calculate them if needed"""
    dirty = False
    if note.title and not note.title_embedding:
        note.set_title_embeddings(get_text_embedding(note.title))
        dirty = True
    if note.comment and not note.content_embedding:
        note.set_content_embeddings(get_text_embedding(note.comment))
        dirty = True

    if dirty:
        print("updating note", note)
        note.save()

    return note


def cosine_similarity(vector1, vector2):
    """Calculate the cosine similarity between two vectors"""
    if len(vector1) != len(vector2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(a**2 for a in vector1))
    magnitude2 = math.sqrt(sum(b**2 for b in vector2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    else:
        return dot_product / (magnitude1 * magnitude2)


def get_note_similarity(note1: Note, note2: Note) -> float:
    """calculate the similarity between 2 notes"""
    max_similarity = 0.0
    # no we need to update embeddings
    update_note_embeddings(note1)
    update_note_embeddings(note2)
    # if there are embeddings and the search vector has embeddings
    if note1.title_embedding and note2.title_embedding:
        title_distance: float = cosine_similarity(
            note1.get_title_embeddings(), note2.get_title_embeddings()
        )
    if note1.content_embedding and note2.content_embedding:

        content_distance: float = cosine_similarity(
            note1.get_content_embeddings(), note2.get_content_embeddings()
        )
        max_similarity = max(max_similarity, title_distance, content_distance)
    return max_similarity

""" Routines for searching notes """

# pylint: disable=no-member

from collections import defaultdict
from dataclasses import dataclass
from doofer.models import Note
from doofer.embeddings import (
    cosine_similarity,
    update_note_embeddings,
    get_text_embedding,
)

THRESHOLD = 0.25
MAX_CACHE_SIZE = 20


@dataclass
class NoteSummaryRecord:
    """mapping a note id to a title"""

    id: str
    title: str


def get_my_notes(uid: str) -> list[Note]:
    """Get all notes for current user"""
    notes = list(Note.objects.filter(user=uid))
    return notes


def get_similar_to_text(text: str, notes: list[Note], count=10):
    """Get notes similar to a text query
    test -- the text to search for
    notes -- the notes to search
    count the max number of notes to return
    Returns the ids of most similar notes sorted by similarity
    """
    text_vector: list[float] = get_text_embedding(text)
    similar_note_ids: list[NoteSummaryRecord] = vecs_similar_ranked(
        [text_vector], notes, "", count
    )
    return similar_note_ids


def get_note_by_id(notes: list[Note], note_id: str) -> Note | None:
    """Get a note by id from a list of notes"""
    str_id = str(note_id)
    note = next((x for x in notes if str(x.id) == str_id), None)  # type: ignore[attr-defined]
    return note


def vecs_similar_ranked(
    vecs: list[list[float]],
    notes: list[Note],
    original_id: str,
    count=10,
    threshold=THRESHOLD,
) -> list[NoteSummaryRecord]:
    """Get the 10 most similar notes to a search vector
    searchVecs -- list of vectors to search for
        (eg title, comment), or maybe just one
    notes[] --  the notes to search through
    originalId --  the id of the note we are searching for, or null
    count --  the number of notes to return
    threshold --  the minimum similarity score to return
    Returns ids of most similar notes sorted by similarity
    """
    similarity_scores: dict[str, float] = defaultdict(float)

    # for a note with embs 'noteVec', calculate the similarity
    for note in notes:
        update_note_embeddings(note)
        for vec in vecs:
            # for a given note and given embedding, calculate the similarity
            score = max(
                cosine_similarity(vec, note.get_title_embeddings()),
                cosine_similarity(vec, note.get_content_embeddings()),
            )
            if abs(score) < 0.0000001:
                print(f"Similarity score : {score} for {note.id} v. {original_id}")

            # keep the highest score
            if score > threshold and score > similarity_scores[note.id]:
                similarity_scores[note.id] = score
    # Sort score scores in descending order
    # -> list of [id, score]
    sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    # Retrieve the top 'count' notes
    # -> list of ids
    ranked_notes = [s[0] for s in sorted_scores[:count]]

    # prepare the return value
    related: list[NoteSummaryRecord] = []
    for note_id in ranked_notes:
        # get the title of the note with id 'id'
        n = get_note_by_id(notes, str(note_id))
        if n:
            related.append(NoteSummaryRecord(str(note_id), n.title))
    return related


def notes_similar_ranked(
    note: Note, notes: list[Note], original_id: str, count=10, threshold=THRESHOLD
) -> list[NoteSummaryRecord]:
    """utility fn to package the note embeddings for search"""

    return vecs_similar_ranked(
        [note.get_title_embeddings(), note.get_content_embeddings()],
        notes,
        original_id,
        count,
        threshold,
    )


def do_text_search(
    search_text: str, uid: str, max_results: float = 10
) -> list[NoteSummaryRecord]:
    """
    * search for text in the notes
    searchText --  the text to search for
    maxResults --  the maximum number of results to return
    uid --  the user id
    Returns  the most similar notes sorted by similarity {id: title}
    """
    notes = get_my_notes(uid)
    results: list[NoteSummaryRecord] = []

    if len(notes) == 0 or not search_text:
        print("textSearch - no notes", uid)
        return results

    # crude text search
    search_text_lower = search_text.lower()
    for note in notes:
        if (
            search_text_lower in note.title.lower()
            or search_text_lower in note.comment.lower()
        ):
            results.append(NoteSummaryRecord(id=str(note.id), title=note.title))

    # if we still don't have enough results, search for similar notes
    if len(results) < max_results:
        search_results = get_similar_to_text(
            search_text, notes, max_results - len(results)
        )
        for result in search_results:
            # only add if the key not already in the list
            if not any(note.id == result.id for note in results):
                results.append(result)

    return results


def do_note_search(
    note_id: str, max_results: float, uid: str, threshold=THRESHOLD
) -> list[NoteSummaryRecord]:
    """Search for text in the notes
    noteId -- ID of the note to compare
    maxResults -- The maximum number of results.
    uid -- The user id.
    threshold -- The minimum similarity score to return.
    Returns the most similar notes sorted by similarity
    """

    # get the note
    notes = get_my_notes(uid)
    # find the note with note.id == noteId
    note = get_note_by_id(notes, note_id)
    if not note:
        print("noteSearch - note not found", {note_id, uid})
        return []

    # only search if there are text fields
    if note.title or note.comment:

        print("noteSearch - getting related")
        # we didn't find a valid cache, so search for related notes

        # if the user has no other notes, return empty
        if len(notes) <= 1:
            return []

        # get embeddings for this note
        note = update_note_embeddings(note)

        # get the most similar notes
        search_results = notes_similar_ranked(
            note, notes, note_id, max_results, threshold
        )
        return search_results
    # as the note has no text fields, return empty
    return []

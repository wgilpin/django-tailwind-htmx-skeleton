from dataclasses import dataclass
from typing import TypeAlias
from doofer.models import Note
from doofer.embeddings import (
    cosine_similarity,
    updateNoteEmbeddings,
    getTextEmbedding,
)
from typing import List
from django.db.models import QuerySet
from doofer.models import Note

THRESHOLD = 0.25
MAX_CACHE_SIZE = 20


@dataclass
class NoteSummaryRecord:
    id: str
    title: str


def getMyNotes(uid: str) -> list[Note]:
    """Get all notes for current user"""
    notes = list(Note.objects.filter(user=uid))
    return notes


def getSimilarToText(text: str, notes: list[Note], count=10):
    """Get notes similar to a text query
    test -- the text to search for
    notes -- the notes to search
    count the max number of notes to return
    Returns the ids of most similar notes sorted by similarity
    """
    textVector: list[float] = getTextEmbedding(text)
    similarNoteIds: list[NoteSummaryRecord] = vecsSimilarRanked(
        [textVector], notes, "", count
    )
    return similarNoteIds


def get_note_by_id(notes: list[Note], id: str) -> Note | None:
    """Get a note by id from a list of notes"""
    note = next((x for x in notes if str(x.id) == id), None)  # type: ignore[attr-defined]
    return note


def vecsSimilarRanked(
    vecs: list[list[float]],
    notes: list[Note],
    originalId: str,
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
    similarityScores: dict[str, float] = {}

    # for a note with embs 'noteVec', calculate the similarity
    for note in notes:
        for vec in vecs:
            # for a given note and given embedding, calculate the similarity
            score = max(
                cosine_similarity(vec, note.title_embedding),
                cosine_similarity(vec, note.content_embedding),
            )
            if abs(score) < 0.0000001:
                print(f"Similarity score : ${score} for ${note.id} v. ${originalId}")

            # keep the highest score
            if score > threshold and score > similarityScores[note.id]:
                similarityScores[note.id] = score
    # Sort score scores in descending order
    # -> list of [id, score]
    sortedScores = sorted(similarityScores.items(), key=lambda x: x[1], reverse=True)

    # Retrieve the top 'count' notes
    # -> list of ids
    rankedNotes = [s[0] for s in sortedScores[:count]]

    # prepare the return value
    related: list[NoteSummaryRecord] = []
    for id in rankedNotes:
        # get the title of the note with id 'id'
        n = get_note_by_id(notes, id)
        if n:
            related.append(NoteSummaryRecord(id, n.title))
    return related


def notesSimilarRanked(
    note: Note, notes: list[Note], originalId: str, count=10, threshold=THRESHOLD
) -> list[NoteSummaryRecord]:
    """utility fn to package the note embeddings for search"""

    return vecsSimilarRanked(
        [note.title_embedding, note.content_embedding],
        notes,
        originalId,
        count,
        threshold,
    )


def doTextSearch(
    searchText: str, maxResults: float, uid: str
) -> list[NoteSummaryRecord]:
    """
    * search for text in the notes
    searchText --  the text to search for
    maxResults --  the maximum number of results to return
    uid --  the user id
    Returns  the most similar notes sorted by similarity {id: title}
    """
    notes = getMyNotes(uid)
    results: list[NoteSummaryRecord] = []

    if len(notes) == 0:
        print("textSearch - no notes", uid)
        return results

    # crude text search
    searchTextLower = searchText.lower()
    for note in notes:
        if note.title.toLowerCase().includes(
            searchTextLower
        ) or note.comment.toLowerCase().includes(searchTextLower):
            results.append(NoteSummaryRecord(id=str(note.id), title=note.title))

    # if we still don't have enough results, search for similar notes
    if len(results) < maxResults:
        searchResults = getSimilarToText(searchText, notes, maxResults - len(results))
        for r in searchResults:
            # only add if the key not already in the list
            temp = NoteSummaryRecord(id=r[0], title=r[1])
            if not temp in results:
                results.append(temp)

    return results


def doNoteSearch(
    noteId: str, maxResults: float, uid: str, threshold=THRESHOLD
) -> list[NoteSummaryRecord]:
    """Search for text in the notes
    noteId -- ID of the note to compare
    maxResults -- The maximum number of results.
    uid -- The user id.
    threshold -- The minimum similarity score to return.
    Returns the most similar notes sorted by similarity
    """

    # get the note
    notes = getMyNotes(uid)
    # find the note with note.id == noteId
    note = get_note_by_id(notes, noteId)
    if not note:
        print("noteSearch - note not found", {noteId, uid})
        return []

    # only search if there are text fields
    if note.title or note.comment:

        print("noteSearch - getting related")
        # we didn't find a valid cache, so search for related notes

        # if the user has no other notes, return empty
        if len(notes) <= 1:
            return []

        # get embeddings for this note
        note = updateNoteEmbeddings(note)

        # get the most similar notes
        searchResults = notesSimilarRanked(note, notes, noteId, maxResults, threshold)
        return searchResults
    else:
        # if the note has no text fields, return empty
        return []


EmbeddingsRecord: TypeAlias = dict[str, list[list[float]]]


def getEmbeddingsForNotes(notes: list[Note], originalId: str) -> EmbeddingsRecord:
    """Get the embeddings for a list of notes
    notes --  the snapshot of the notes
    originalId --  the id of the note to exclude from the results
    Returns the embeddings for the notes
    """
    vecs: EmbeddingsRecord = {}
    for n in notes:
        if n.id != originalId:
            updated = updateNoteEmbeddings(n)
            vecs[n.id] = [updated.title_embedding, updated.content_embedding]

    return vecs

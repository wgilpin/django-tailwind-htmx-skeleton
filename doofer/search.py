from typing import Any, TypeAlias
from doofer.models import Note
from doofer.embeddings import (
    cosine_similarity,
    updateNoteEmbeddings,
    getNoteSimilarity,
    getTextEmbedding,
)
from typing import List
from django.db.models import QuerySet
from doofer.models import (
    Note,
)  # Add this line to import the "Note" model from the "doofer" module

THRESHOLD = 0.25
MAX_CACHE_SIZE = 20

NoteSummary: TypeAlias = List[str]

"""
* Convert a list of noteSummary to a list of objects with id and title
 * @param {NoteSummary[]} summaries
 * @return {object[]} list of objects
"""


def noteSummariesToIds(summaries: list[NoteSummary]) -> list[dict[str, str]]:
    res: list[dict[str, str]] = []
    for s in summaries:
        res.append({"id": s[0], "title": s[1]})
    return res


"""
 * get all notes for current user
 * @param {string} uid the user id
 * @return {Promise<QuerySnapshot>} the notes
"""


def getMyNotes(uid: str) -> list[Note]:
    notes = list(Note.objects.filter(user=uid))
    return notes


"""
 * get notes similar to a text query
 * @param {string} text the text to search for
 * @param {myNotes} notes the notes to search
 * @param {number} count the max number of notes to return
 * @return {string[]} ids of most similar notes sorted by similarity
"""


def getSimilarToText(text: str, notes: list[Note], count=10):
    textVector: list[float] = getTextEmbedding(text)
    similarNoteIds: list[NoteSummary] = vecsSimilarRanked(
        [textVector], notes, "", count
    )
    return similarNoteIds


def get_note_by_id(notes: list[Note], id: str) -> Note | None:
    note = next((x for x in notes if str(x.id) == id), None)  # type: ignore[attr-defined]
    return note




"""
 * get the 10 most similar notes to a search vector
 * @param {Array<number[]>} searchVecs array of the vectors to search for
 * (eg title, snippet, comment), or maybe just one
 * @param {QueryDocumentSnapshot[]} notes the notes to search through
 * @param {string} originalId the id of the note we are searching for, or null
 * @param {number} count the number of notes to return
 * @param {number} threshold the minimum similarity score to return
 * @return {NoteSummary[]} ids of most similar notes sorted by similarity
"""


def vecsSimilarRanked(
    vecs: list[list[float]],
    notes: list[Note],
    originalId: str,
    count=10,
    threshold=THRESHOLD,
) -> list[NoteSummary]:
    similarityScores: dict[str, float] = {}  # id: score
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
    related: list[NoteSummary] = []
    for id in rankedNotes:
        # get the title of the note with id 'id'
        n = get_note_by_id(notes, id)
        if n:
            related.append([id, n.title])
    return related


""" utility fn to package the note embeddings for search """


def notesSimilarRanked(
    note: Note, notes: list[Note], originalId: str, count=10, threshold=THRESHOLD
) -> list[NoteSummary]:
    return vecsSimilarRanked(
        [note.title_embedding, note.content_embedding],
        notes,
        originalId,
        count,
        threshold,
    )


"""
 * search for text in the notes
 * @param {string} searchText the text to search for
 * @param {number} maxResults the maximum number of results to return
 * @param {string} uid the user id
 * @return {object[]} the most similar notes sorted by similarity {id: title}
"""


def doTextSearch(searchText: str, maxResults: float, uid: str) -> list[Any]:
    notes = getMyNotes(uid)
    results: list[NoteSummary] = []

    if len(notes) == 0:
        print("textSearch - no notes", uid)
        return results

    # crude text search
    searchTextLower = searchText.lower()
    for note in notes:
        if note.title.toLowerCase().includes(
            searchTextLower
        ) or note.comment.toLowerCase().includes(searchTextLower):
            results.append([note.id, note.title])

    # if we still don't have enough results, search for similar notes
    if len(results) < maxResults:
        searchResults = getSimilarToText(searchText, notes, maxResults - len(results))
        for r in searchResults:
            # only add if the key not already in the list
            temp = [r[0], r[1]]
            if not temp in results:
                results.append(temp)

    return noteSummariesToIds(results)


"""
   * search for text in the notes
   * @param {string} noteId - ID of the note to compare
   * @param {number} maxResults - The maximum number of results.
   * @param {string} uid - The user id.
   * @param {number} threshold - The minimum similarity score to return.
   * @return {object[]} the most similar notes sorted by similarity
  """


def doNoteSearch(
    noteId: str, maxResults: float, uid: str, threshold=THRESHOLD
) -> list[Any]:
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
        return noteSummariesToIds(searchResults)
    else:
        # if the note has no text fields, return empty
        return []


EmbeddingsRecord: TypeAlias = dict[str, list[list[float]]]

"""
 * get the embeddings for a list of notes
 * @param {DocumentSnapshot} notes the snapshot of the notes
 * @param {string} originalId the id of the note to exclude from the results
 * @return {object} the embeddings for the notes
 """


def getEmbeddingsForNotes(notes: list[Note], originalId: str) -> EmbeddingsRecord:
    vecs: EmbeddingsRecord = {}
    for n in notes:
        if n.id != originalId:
            updated = updateNoteEmbeddings(n)
            vecs[n.id] = [updated.title_embedding, updated.content_embedding]

    return vecs

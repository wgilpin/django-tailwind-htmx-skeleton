from doofer.models import Note

from fixtures import user_1, note_1, note_2, note_3


def test_get_title_embeddings(note_1, note_2, note_3):
    note_2.set_title_embeddings([0.1, 0.1, 0.2, 0.3])
    note_3.set_title_embeddings([0.1, 0.1, 0.2, 0.3])

    note_1_embeddings = [0.1, 0.2, 0.3]
    note_1.set_title_embeddings(note_1_embeddings)
    assert note_1.get_title_embeddings() == note_1_embeddings

    note_2_embeddings = []
    note_2.set_title_embeddings(note_2_embeddings)
    assert note_2.get_title_embeddings() == note_2_embeddings

    note_3_embeddings = [0.9]
    note_3.set_title_embeddings(note_3_embeddings)
    assert note_3.get_title_embeddings() == note_3_embeddings

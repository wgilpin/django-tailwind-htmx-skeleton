from doofer.models import Note

def test_get_title_embeddings():
    note = Note(title_embedding='0.1,0.2,0.3')
    expected_embeddings = [0.1, 0.2, 0.3]
    assert note.get_title_embeddings() == expected_embeddings

    note = Note(title_embedding='0.5,0.6,0.7,0.8')
    expected_embeddings = [0.5, 0.6, 0.7, 0.8]
    assert note.get_title_embeddings() == expected_embeddings

    note = Note(title_embedding='')
    expected_embeddings = []
    assert note.get_title_embeddings() == expected_embeddings

    note = Note(title_embedding='0.9')
    expected_embeddings = [0.9]
    assert note.get_title_embeddings() == expected_embeddings

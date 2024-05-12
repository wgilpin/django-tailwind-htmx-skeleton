import json
import math
import os
import time
import requests

from typing import TypeAlias
from typing import Dict, List
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from doofer.models import Note

HF_MODEL = 'all-MiniLM-L6-v2'
EMBEDDINGS_SIZE = 384

model = None

"""
 * get the embedding from hugging face
 * @param {str} text the text to embed
 * @return {Promise<number[]>} the embedding
"""
def getHFembeddings(text: str) -> list[float]:
  global model
  
  load_dotenv()
  token = os.getenv('API_TOKEN')
  
  try:
    if not model:
      model = SentenceTransformer(f'sentence-transformers/{HF_MODEL}', token=token)
      
    embeddings = model.encode(text)
    return list(embeddings)
  except Exception as error:
    print('hf error', error)
    return []

"""
   * get the embedding from openai
   * @param {str} text the text to embed
   * @param {boolean} useCache whether to use the cache
   * @return {Promise<number[]>} the embedding
   * @see https:#beta.openai.com/docs/api-reference/retrieve-embedding
  """
def getTextEmbedding(text: str) -> list[float]:
  try:
    vector: list[float] = getHFembeddings(text)
    return vector
  except Exception as error:
    print('API  error', {error})
    return []




def updateNoteEmbeddings(note: Note) -> Note:
    # get the note embeddings from the db or calculate them if needed
    dirty = False
    if note.title and not note.title_embedding:
        note.set_title_embeddings(getTextEmbedding(note.title))
        dirty = True
    if note.comment and not note.content_embedding:
        note.set_content_embeddings(getTextEmbedding(note.comment))
        dirty = True

    if dirty:
        note.save()
        
    return note

def cosine_similarity(vector1, vector2):
  """
  Calculate the cosine similarity between two vectors.

  Args:
    vector1 (list): The first vector.
    vector2 (list): The second vector.

  Returns:
    float: The cosine similarity between the two vectors.
  """
  if len(vector1) != len(vector2):
    return 0.0
  
  dot_product = sum(a * b for a, b in zip(vector1, vector2))
  magnitude1 = math.sqrt(sum(a ** 2 for a in vector1))
  magnitude2 = math.sqrt(sum(b ** 2 for b in vector2))

  if magnitude1 == 0 or magnitude2 == 0:
    return 0.0
  else:
    return dot_product / (magnitude1 * magnitude2)


"""
  * calculate the similarity between 2 notes
"""
def getNoteSimilarity(note1: Note, note2: Note) ->float:
  maxSimilarity = 0.0
  # no we need to update embeddings
  updateNoteEmbeddings(note1)
  updateNoteEmbeddings(note2)
  # if there are embeddings and the search vector has embeddings
  if note1.title_embedding and note2.title_embedding:
      titleDistance: float = cosine_similarity(note1.get_title_embeddings(), note2.get_title_embeddings())
  if note1.content_embedding and note2.content_embedding:
  
      contentDistance: float = cosine_similarity(note1.get_content_embeddings(), note2.get_content_embeddings())
      maxSimilarity = max(maxSimilarity, titleDistance, contentDistance)
  return maxSimilarity
import json
import math
import os
import time
import requests

from typing import TypeAlias
from typing import Dict, List

from doofer.models import Note


HF_SECRET_NAME = 'HF_API_KEY/versions/1'

def fetch(url: str, options: dict = {}) -> requests.Response:
  """
  A polyfill for the fetch() function in JavaScript.

  Args:
    url (str): The URL to fetch.
    options (dict): The options to pass to the request.

  Returns:
    requests.Response: The response from the request.
  """

  # Set default options
  default_options = {
    "method": "GET",
    "headers": {},
    "body": None,
  }
  options = {**default_options, **options}

  # Make the request
  response = requests.request(**options)

  # Return the response
  return response


"""
 * get the embedding from hugging face
 * @param {str} text the text to embed
 * @return {Promise<number[]>} the embedding
"""
def getHFembeddings(text: str) -> list[float]:
  model = 'all-MiniLM-L6-v2'
  apiUrl = f'https:#api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/${model}'
  data = {"inputs": text, "wait_for_model": True}
  
  hfToken = os.getenv(HF_SECRET_NAME) or ""
  if not hfToken:
    raise Exception('HF_API_KEY not found in environment')
  
  retries = 4
  while retries > 0:
    try:
      # call the api
      response = fetch(apiUrl, {"headers": {"Authorization": f'Bearer ${hfToken}',"pragma": 'no-cache', 'cache-control': 'no-cache',
        },
        "method": 'POST',
        "body": json.dumps(data),
      })
      res = response.json()
      if res.error:
        raise Exception(res.error)

      return res
    except Exception as error:
      print('hf error', {error})
      retries -= 1
      # wait 7 seconds before retrying  
      time.sleep(7)
      continue
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
        note.title_embedding = getTextEmbedding(note.title)
        dirty = True
    if note.comment and not note.content_embedding:
        note.content_embedding = getTextEmbedding(note.comment)
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
    
  # if there are embeddings and the search vector has embeddings
  if note1.title_embedding and note2.title_embedding:
      titleDistance: float = cosine_similarity(note1.get_title_embeddings(), note2.get_title_embeddings())
  if note1.content_embedding and note2.content_embedding:
  
      contentDistance: float = cosine_similarity(note1.get_content_embeddings(), note2.get_content_embeddings())
      maxSimilarity = max(maxSimilarity, titleDistance, contentDistance)
  return maxSimilarity
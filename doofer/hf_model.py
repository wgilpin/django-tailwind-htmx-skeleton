""" A class to load the Hugging Face model and get embeddings for a given text """

import os
from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
from dotenv import load_dotenv

HF_MODEL = "all-MiniLM-L6-v2"


class HFModel:
    """A singleton class to load the Hugging Face model and get embeddings for a given text"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HFModel, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """load the Hugging Face model"""
        if self._model is None:
            load_dotenv("secrets.env")
            token = os.getenv("API_TOKEN")
            self._model = SentenceTransformer(
                f"sentence-transformers/{HF_MODEL}", token=token
            )
        return self._model


def get_hf_embeddings(text: str) -> list[float]:
    """Get the embeddings for a given text using the Hugging Face model"""
    try:
        model = HFModel().load_model()
        embeddings = model.encode(text)
        return list(embeddings)
    except Exception as error:
        print("hf error", error)
        return []

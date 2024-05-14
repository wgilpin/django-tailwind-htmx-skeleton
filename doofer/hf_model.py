""" A class to load the Hugging Face model and get embeddings for a given text """

import json
import os
from dotenv import load_dotenv
import requests
import time

HF_MODEL = "all-MiniLM-L6-v2"


class HFKey:
    """A singleton class to load the Hugging Face API Key"""

    _instance = None
    _token: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HFKey, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """load the env var"""
        if self._token is None:
            load_dotenv("secrets.env")
            self._token = os.getenv("API_TOKEN")
        return self._token


def get_hf_embeddings(text: str) -> list[float]:
    """Get the embeddings for a given text using the Hugging Face model"""
    model = "all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/{model}"
    data = {"inputs": text, "wait_for_model": True}
    hf_token: str = HFKey().load_model()
    retries = 4
    while retries > 0:
        # call the api
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "pragma": "no-cache",
            "cache-control": "no-cache",
        }

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

            # Now you can work with the response data
            if response.status_code == 200:
                result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")

        retries -= 1
        # wait 5 seconds before retrying
        time.sleep(5)
    print("API rety limit reached. Exiting...")
    return []

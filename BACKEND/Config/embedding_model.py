from langchain_huggingface import HuggingFaceEmbeddings
from BACKEND.Config.config import EMBEDDING_MODEL

_embeddings = None

def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Load and return the embedding model.

    The model is loaded only once and then reused.

    This prevents repeatedly loading the Sentence Transformer
    model during the application lifetime.
    """

    global _embeddings

    if _embeddings is None:

        print(f"Loading embedding model:{EMBEDDING_MODEL}")

        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        print("Embedding model loaded successfully.")

    return _embeddings
from qdrant_client import QdrantClient, models

from BACKEND.Config.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
)


# ============================================================
# QDRANT CONFIGURATION
# ============================================================

# sentence-transformers/all-MiniLM-L6-v2
QDRANT_DENSE_DIMENSION = 384

QDRANT_DENSE_DISTANCE = models.Distance.COSINE

QDRANT_DENSE_NAME = "dense"


# ============================================================
# CACHED CLIENT
# ============================================================

_qdrant_client = None


# ============================================================
# GET QDRANT CLIENT
# ============================================================

def get_qdrant_client() -> QdrantClient:
    """
    Create and return the Qdrant client.

    The client is initialized only once
    and then reused.
    """

    global _qdrant_client

    # --------------------------------------------------------
    # Reuse cached client
    # --------------------------------------------------------

    if _qdrant_client is not None:
        return _qdrant_client

    # --------------------------------------------------------
    # Validate configuration
    # --------------------------------------------------------

    if not QDRANT_URL:
        raise ValueError(
            "QDRANT_URL is not set."
        )

    if not QDRANT_API_KEY:
        raise ValueError(
            "QDRANT_API_KEY is not set."
        )

    # --------------------------------------------------------
    # Initialize client
    # --------------------------------------------------------

    try:

        print(
            "Initializing Qdrant client..."
        )

        # TEMPORARY DEBUGGING
        # Do NOT print the actual API key.
        print(
            "QDRANT_URL:",
            repr(QDRANT_URL)
        )

        print(
            "QDRANT_API_KEY exists:",
            bool(QDRANT_API_KEY)
        )

        _qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

        print(
            "Qdrant client initialized successfully."
        )

        return _qdrant_client

    except Exception as e:

        raise RuntimeError(
            "Failed to initialize Qdrant client: "
            f"{str(e)}"
        ) from e


# ============================================================
# CREATE / GET COLLECTION
# ============================================================

def get_qdrant_collection():
    """
    Create the HR Copilot Qdrant collection
    if it does not exist.

    Qdrant stores only dense embeddings.

    Dense embedding model:

        sentence-transformers/all-MiniLM-L6-v2

    Dense vector:

        name      = dense
        dimension = 384
        distance  = cosine

    BM25 is handled separately using PostgreSQL
    and is NOT stored as a sparse vector in Qdrant.
    """

    client = get_qdrant_client()

    try:

        # ----------------------------------------------------
        # Check existing collections
        # ----------------------------------------------------

        collections = client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        # ----------------------------------------------------
        # Reuse existing collection
        # ----------------------------------------------------

        if QDRANT_COLLECTION_NAME in collection_names:

            print(
                f"\nQdrant collection already exists: "
                f"{QDRANT_COLLECTION_NAME}"
            )

            return client

        # ----------------------------------------------------
        # Create collection
        # ----------------------------------------------------

        print(
            f"\nCreating Qdrant collection: "
            f"{QDRANT_COLLECTION_NAME}"
        )

        print(
            f"Dense vector name: "
            f"{QDRANT_DENSE_NAME}"
        )

        print(
            f"Dense dimension: "
            f"{QDRANT_DENSE_DIMENSION}"
        )

        print(
            f"Dense distance: "
            f"{QDRANT_DENSE_DISTANCE}"
        )

        # ----------------------------------------------------
        # Create dense-only collection
        # ----------------------------------------------------

        client.create_collection(

            collection_name=QDRANT_COLLECTION_NAME,

            vectors_config={
                QDRANT_DENSE_NAME: models.VectorParams(
                    size=QDRANT_DENSE_DIMENSION,
                    distance=QDRANT_DENSE_DISTANCE,
                )
            },
        )

        print(
            "\nQdrant collection created successfully."
        )

        return client

    except Exception as e:

        raise RuntimeError(
            "Failed to create/get Qdrant collection: "
            f"{str(e)}"
        ) from e


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("QDRANT COLLECTION TEST")
    print("=" * 70)

    client = get_qdrant_collection()

    print(
        "\nQdrant connection successful."
    )

    print(
        f"Collection name: "
        f"{QDRANT_COLLECTION_NAME}"
    )

    print(
        f"Dense vector: "
        f"{QDRANT_DENSE_NAME}"
    )

    print(
        f"Dense dimension: "
        f"{QDRANT_DENSE_DIMENSION}"
    )

    print(
        f"Dense distance: "
        f"{QDRANT_DENSE_DISTANCE}"
    )

    print(
        "\nBM25: PostgreSQL"
    )

    print(
        "Qdrant sparse vector: Not used"
    )

    print("\n" + "=" * 70)
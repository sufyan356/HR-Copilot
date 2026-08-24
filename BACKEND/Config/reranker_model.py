from typing import Optional
from sentence_transformers import CrossEncoder
from BACKEND.Config.config import RERANKER_MODEL


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_TOP_K = 5


# ============================================================
# CACHED RERANKER
# ============================================================

_reranker: Optional[CrossEncoder] = None


# ============================================================
# GET RERANKER
# ============================================================

def get_reranker() -> CrossEncoder:
    """
    Load the CrossEncoder reranker only once.

    The reranker compares:

        query + candidate chunk text

    and produces a relevance score.
    """

    global _reranker

    # --------------------------------------------------------
    # Reuse cached model
    # --------------------------------------------------------

    if _reranker is not None:
        return _reranker

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print(
        f"Loading reranker model: "
        f"{RERANKER_MODEL}"
    )

    _reranker = CrossEncoder(
        RERANKER_MODEL
    )

    print(
        "Reranker model loaded successfully."
    )

    return _reranker
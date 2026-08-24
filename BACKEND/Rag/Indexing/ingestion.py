#                   INDEXING

# PDF / Excel
#      ↓
#    Loader
#      ↓
# Normalizer
#      ↓
#   Chunker
#      ↓
#  ┌───┴──────────────┐
#  ▼                  ▼
# PostgreSQL        Qdrant
# metadata          Dense 384
# chunk text        vector


# Retrieval

#                     QUERY
#                       │
#              ┌────────┴────────┐
#              ▼                 ▼
#             BM25             Qdrant
#         PostgreSQL           Dense
#              │                 │
#              └────────┬────────┘
#                       ▼
#                    Merge
#                       ↓
#                   Reranker
#                       ↓
#                      LLM



from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from langchain_core.documents import Document
from qdrant_client.models import PointStruct

from BACKEND.Rag.Indexing.loader import load_file
from BACKEND.Rag.Indexing.normalizer import normalize_documents
from BACKEND.Rag.Indexing.chunker import chunk_documents
from BACKEND.Rag.Indexing.embeddings import embed_documents

from BACKEND.Config.qdrant_index import get_qdrant_collection
from BACKEND.Config.config import QDRANT_COLLECTION_NAME

from BACKEND.Models.model import ContextChunks
from BACKEND.Database.database import session_local


# ============================================================
# FILE PATHS
# ============================================================

EXCEL_PATH = r"BACKEND\Data\hr-policy-data.xlsx"

PDF_PATH = r"BACKEND\Data\hr-policy.pdf"


# ============================================================
# BUILD QDRANT POINTS
# ============================================================

def build_qdrant_points(
    chunks: List[Document],
    embeddings: List[List[float]],
) -> List[PointStruct]:
    """
    Build Qdrant points from chunks and dense embeddings.

    Each Qdrant point contains:

        id
            Same chunk_id used by PostgreSQL.

        vector
            384-dimensional dense embedding.

        payload
            Metadata + chunk text.

    Qdrant does NOT store the original embedding model.
    It stores the generated vector.
    """

    if len(chunks) != len(embeddings):

        raise ValueError(
            "Number of chunks and embeddings "
            "must be identical."
        )

    points = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):

        metadata = chunk.metadata

        # ----------------------------------------------------
        # Get metadata
        # ----------------------------------------------------

        chunk_id = metadata.get(
            "chunk_id"
        )

        doc_id = metadata.get(
            "doc_id"
        )

        if not chunk_id:

            raise ValueError(
                "Chunk is missing chunk_id."
            )

        if not doc_id:

            raise ValueError(
                "Chunk is missing doc_id."
            )

        # ----------------------------------------------------
        # Validate embedding dimension
        # ----------------------------------------------------

        if len(embedding) != 384:

            raise ValueError(
                f"Invalid embedding dimension "
                f"for chunk {chunk_id}. "
                f"Expected 384, "
                f"received {len(embedding)}."
            )

        # ----------------------------------------------------
        # Qdrant payload
        # ----------------------------------------------------

        payload = {

            "chunk_id": chunk_id,

            "doc_id": doc_id,

            "user_id": metadata.get(
                "user_id"
            ),

            "source": metadata.get(
                "file_name"
            ),

            "file_name": metadata.get(
                "file_name"
            ),

            "file_type": metadata.get(
                "file_type"
            ),

            "page_number": metadata.get(
                "page_number"
            ),

            "row_number": metadata.get(
                "row_number"
            ),
        }

        # ----------------------------------------------------
        # Create Qdrant point
        # ----------------------------------------------------

        point = PointStruct(

            id=chunk_id,

            vector={
                "dense": embedding
            },

            payload=payload,
        )

        points.append(point)

    return points


# ============================================================
# STORE CHUNKS IN POSTGRESQL
# ============================================================

def add_chunks_to_database(
    db,
    chunks: List[Document],
    user_id: Optional[int] = None,
) -> List[ContextChunks]:
    """
    Create PostgreSQL ContextChunks objects.

    NOTE:

    This function does NOT commit.

    The caller commits only after Qdrant
    indexing succeeds.
    """

    db_chunks = []

    for chunk in chunks:

        metadata = chunk.metadata

        context_chunk = ContextChunks(

            doc_id=metadata.get(
                "doc_id"
            ),

            chunk_id=metadata.get(
                "chunk_id"
            ),

            user_id=user_id,

            chunk_text=chunk.page_content,

            source=metadata.get(
                "file_name"
            ),

            file_name=metadata.get(
                "file_name"
            ),

            file_type=metadata.get(
                "file_type"
            ),

            page_number=metadata.get(
                "page_number"
            ),

            row_number=metadata.get(
                "row_number"
            ),
        )

        db.add(
            context_chunk
        )

        db_chunks.append(
            context_chunk
        )

    return db_chunks


# ============================================================
# STORE VECTORS IN QDRANT
# ============================================================

def store_vectors_in_qdrant(
    points: List[PointStruct],
) -> None:
    """
    Upload dense vectors to Qdrant.

    PostgreSQL:
        chunk_id → chunk text + metadata

    Qdrant:
        chunk_id → dense vector + payload
    """

    if not points:

        raise ValueError(
            "No Qdrant points provided."
        )

    client = get_qdrant_collection()

    print(
        "\nUploading vectors to Qdrant..."
    )

    client.upsert(

        collection_name=QDRANT_COLLECTION_NAME,

        points=points,
    )

    print(
        f"Qdrant vectors stored: "
        f"{len(points)}"
    )


# ============================================================
# INGEST SINGLE FILE
# ============================================================

def ingest_file(
    file_path: str,
    user_id: Optional[int] = None,
) -> dict:
    """
    Run the complete indexing pipeline for one file.

    Pipeline:

        File
          ↓
        Loader
          ↓
        Normalizer
          ↓
        Chunker
          ↓
        Dense Embeddings
          ↓
        Qdrant
          +
        PostgreSQL

    Parameters
    ----------
    file_path:
        PDF or Excel file path.

    user_id:
        Current authenticated user.

        For our current global HR policy files:

            user_id=None
    """

    file_name = Path(
        file_path
    ).name

    print("\n" + "=" * 70)

    print(
        f"STARTING INGESTION: "
        f"{file_name}"
    )

    print("=" * 70)

    # ========================================================
    # 1. LOAD
    # ========================================================

    print("\n[1/6] Loading file...")

    documents = load_file(
        file_path
    )

    if not documents:

        raise ValueError(
            f"No documents loaded from "
            f"{file_path}"
        )

    print(
        f"Loaded documents: "
        f"{len(documents)}"
    )

    # ========================================================
    # 2. NORMALIZE
    # ========================================================

    print("\n[2/6] Normalizing documents...")

    normalized_documents = normalize_documents(
        documents
    )

    if not normalized_documents:

        raise ValueError(
            f"No documents remained after "
            f"normalization: {file_path}"
        )

    print(
        f"Normalized documents: "
        f"{len(normalized_documents)}"
    )

    # ========================================================
    # 3. CREATE DOC ID
    # ========================================================

    print("\n[3/6] Creating document ID...")

    # One doc_id for one physical file.

    doc_id = str(
        uuid4()
    )

    print(
        f"doc_id: {doc_id}"
    )

    # ========================================================
    # 4. CHUNK
    # ========================================================

    print("\n[4/6] Creating chunks...")

    chunks = chunk_documents(

        normalized_documents,

        doc_id,
    )

    if not chunks:

        raise ValueError(
            f"No chunks created from "
            f"{file_path}"
        )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    # ========================================================
    # 5. EMBEDDINGS
    # ========================================================

    print(
        "\n[5/6] Generating dense embeddings..."
    )

    embeddings = embed_documents(
        chunks
    )

    if not embeddings:

        raise ValueError(
            "No embeddings generated."
        )

    # --------------------------------------------------------
    # Validate count
    # --------------------------------------------------------

    if len(embeddings) != len(chunks):

        raise ValueError(
            "Embedding count does not match "
            "chunk count."
        )

    # --------------------------------------------------------
    # Validate dimension
    # --------------------------------------------------------

    embedding_dimension = len(
        embeddings[0]
    )

    print(
        f"Embeddings generated: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{embedding_dimension}"
    )

    if embedding_dimension != 384:

        raise ValueError(
            "Embedding dimension mismatch. "
            f"Expected 384, "
            f"received {embedding_dimension}."
        )

    # ========================================================
    # BUILD QDRANT POINTS
    # ========================================================

    print(
        "\nBuilding Qdrant points..."
    )

    qdrant_points = build_qdrant_points(

        chunks,

        embeddings,
    )

    print(
        f"Qdrant points prepared: "
        f"{len(qdrant_points)}"
    )

    # ========================================================
    # DATABASE SESSION
    # ========================================================

    db = session_local()

    try:

        # ====================================================
        # ADD TO POSTGRESQL
        # ====================================================

        print(
            "\nPreparing PostgreSQL records..."
        )

        db_chunks = add_chunks_to_database(

            db,

            chunks,

            user_id=user_id,
        )

        print(
            f"PostgreSQL records prepared: "
            f"{len(db_chunks)}"
        )

        # ====================================================
        # QDRANT
        # ====================================================

        store_vectors_in_qdrant(
            qdrant_points
        )

        # ====================================================
        # POSTGRESQL COMMIT
        # ====================================================

        print(
            "\nCommitting PostgreSQL transaction..."
        )

        db.commit()

        print(
            "PostgreSQL transaction committed successfully."
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print("\n" + "-" * 70)

        print(
            f"SUCCESS: {file_name}"
        )

        print("-" * 70)

        return {

            "status": "success",

            "file_name": file_name,

            "file_type": Path(
                file_path
            ).suffix.lower(),

            "doc_id": doc_id,

            "user_id": user_id,

            "documents_loaded": len(
                documents
            ),

            "documents_normalized": len(
                normalized_documents
            ),

            "chunks_created": len(
                chunks
            ),

            "embeddings_created": len(
                embeddings
            ),

            "embedding_dimension":
                embedding_dimension,

            "qdrant_points": len(
                qdrant_points
            ),
        }

    except Exception as e:

        # ====================================================
        # ROLLBACK
        # ====================================================

        print(
            "\nERROR OCCURRED."
        )

        print(
            "Rolling back PostgreSQL transaction..."
        )

        db.rollback()

        print(
            "PostgreSQL rollback completed."
        )

        raise RuntimeError(

            f"Ingestion failed for "
            f"{file_name}: {str(e)}"

        ) from e

    finally:

        # ====================================================
        # CLOSE DATABASE
        # ====================================================

        db.close()

        print(
            "Database connection closed."
        )


# ============================================================
# INGEST MULTIPLE FILES
# ============================================================

def ingest_files(
    file_paths: List[str],
    user_id: Optional[int] = None,
) -> List[dict]:
    """
    Ingest multiple files.

    Each physical file receives its own doc_id.
    """

    results = []

    for file_path in file_paths:

        result = ingest_file(

            file_path=file_path,

            user_id=user_id,
        )

        results.append(
            result
        )

    return results


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n")

    print("#" * 70)

    print(
        "HR COPILOT - RAG INGESTION TEST"
    )

    print("#" * 70)

    # ========================================================
    # FILE PATHS
    # ========================================================

    excel_path = (
        r"BACKEND\Data\hr-policy-data.xlsx"
    )

    pdf_path = (
        r"BACKEND\Data\hr-policy.pdf"
    )

    # ========================================================
    # FILES
    # ========================================================

    file_paths = [

        pdf_path,

        excel_path,
    ]

    # ========================================================
    # INGEST
    # ========================================================

    results = ingest_files(

        file_paths=file_paths,

        # Current HR policy files are global.
        #
        # Therefore:
        #
        # user_id = None

        user_id=None,
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n")

    print("#" * 70)

    print(
        "INGESTION SUMMARY"
    )

    print("#" * 70)

    total_chunks = 0

    total_embeddings = 0

    total_qdrant_points = 0

    # ========================================================
    # PRINT EACH FILE
    # ========================================================

    for result in results:

        print("\n" + "-" * 70)

        print(
            f"File: "
            f"{result['file_name']}"
        )

        print(
            f"Type: "
            f"{result['file_type']}"
        )

        print(
            f"doc_id: "
            f"{result['doc_id']}"
        )

        print(
            f"Documents loaded: "
            f"{result['documents_loaded']}"
        )

        print(
            f"Documents normalized: "
            f"{result['documents_normalized']}"
        )

        print(
            f"Chunks created: "
            f"{result['chunks_created']}"
        )

        print(
            f"Embeddings created: "
            f"{result['embeddings_created']}"
        )

        print(
            f"Embedding dimension: "
            f"{result['embedding_dimension']}"
        )

        print(
            f"Qdrant points: "
            f"{result['qdrant_points']}"
        )

        total_chunks += (
            result["chunks_created"]
        )

        total_embeddings += (
            result["embeddings_created"]
        )

        total_qdrant_points += (
            result["qdrant_points"]
        )

    # ========================================================
    # FINAL TOTALS
    # ========================================================

    print("\n")

    print("#" * 70)

    print(
        "FINAL TOTALS"
    )

    print("#" * 70)

    print(
        f"Files processed: "
        f"{len(results)}"
    )

    print(
        f"Total chunks: "
        f"{total_chunks}"
    )

    print(
        f"Total embeddings: "
        f"{total_embeddings}"
    )

    print(
        f"Total Qdrant points: "
        f"{total_qdrant_points}"
    )

    print(
        "\nIngestion pipeline completed successfully."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
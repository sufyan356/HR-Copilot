from typing import List

from langchain_core.documents import Document

from BACKEND.Config.embedding_model import get_embedding_model


# ============================================================
# EMBED DOCUMENTS
# ============================================================

def embed_documents(
    documents: List[Document],
) -> List[List[float]]:
    """
    Generate embeddings for a list of LangChain Documents.

    The embedding model is loaded from:
        BACKEND.Config.embedding

    The model itself is loaded only once and reused.
    """

    if not documents:
        return []

    embedding_model = get_embedding_model()

    texts = [
        document.page_content
        for document in documents
    ]

    embeddings = embedding_model.embed_documents(
        texts
    )

    return embeddings


# ============================================================
# EMBED QUERY
# ============================================================

def embed_query(
    query: str,
) -> List[float]:
    """
    Generate an embedding for a user query.

    This function will later be used during retrieval.
    """

    embedding_model = get_embedding_model()

    embedding = embedding_model.embed_query(
        query
    )

    return embedding


# ============================================================
# MAIN
# ============================================================

# def main():

#     from BACKEND.Rag.Indexing.loader import load_file
#     from BACKEND.Rag.Indexing.normalizer import normalize_documents
#     from BACKEND.Rag.Indexing.chunker import chunk_documents
#     from uuid import uuid4

#     # ========================================================
#     # FILE PATHS
#     # ========================================================

#     excel_path = r"BACKEND\Data\hr-policy-data.xlsx"
#     pdf_path = r"BACKEND\Data\hr-policy.pdf"

#     # ========================================================
#     # LOAD PDF
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("LOADING PDF")
#     print("#" * 70)

#     pdf_documents = load_file(
#         pdf_path
#     )

#     print(
#         f"PDF pages loaded: "
#         f"{len(pdf_documents)}"
#     )

#     # ========================================================
#     # NORMALIZE PDF
#     # ========================================================

#     normalized_pdf = normalize_documents(
#         pdf_documents
#     )

#     print(
#         f"PDF documents normalized: "
#         f"{len(normalized_pdf)}"
#     )

#     # ========================================================
#     # CHUNK PDF
#     # ========================================================

#     pdf_doc_id = str(uuid4())

#     pdf_chunks = chunk_documents(
#         normalized_pdf,
#         pdf_doc_id,
#     )

#     print(
#         f"PDF chunks created: "
#         f"{len(pdf_chunks)}"
#     )

#     # ========================================================
#     # LOAD EXCEL
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("LOADING EXCEL")
#     print("#" * 70)

#     excel_documents = load_file(
#         excel_path
#     )

#     print(
#         f"Excel rows loaded: "
#         f"{len(excel_documents)}"
#     )

#     # ========================================================
#     # NORMALIZE EXCEL
#     # ========================================================

#     normalized_excel = normalize_documents(
#         excel_documents
#     )

#     print(
#         f"Excel documents normalized: "
#         f"{len(normalized_excel)}"
#     )

#     # ========================================================
#     # CHUNK EXCEL
#     # ========================================================

#     excel_doc_id = str(uuid4())

#     excel_chunks = chunk_documents(
#         normalized_excel,
#         excel_doc_id,
#     )

#     print(
#         f"Excel chunks created: "
#         f"{len(excel_chunks)}"
#     )

#     # ========================================================
#     # COMBINE CHUNKS
#     # ========================================================

#     all_chunks = (
#         pdf_chunks +
#         excel_chunks
#     )

#     print("\n")
#     print("#" * 70)
#     print("GENERATING EMBEDDINGS")
#     print("#" * 70)

#     print(
#         f"Total chunks: "
#         f"{len(all_chunks)}"
#     )

#     # ========================================================
#     # GENERATE DOCUMENT EMBEDDINGS
#     # ========================================================

#     embeddings = embed_documents(
#         all_chunks
#     )

#     # ========================================================
#     # VALIDATION
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("EMBEDDING TEST RESULTS")
#     print("#" * 70)

#     print(
#         f"Documents embedded: "
#         f"{len(embeddings)}"
#     )

#     if embeddings:

#         print(
#             f"Embedding dimension: "
#             f"{len(embeddings[0])}"
#         )

#         print(
#             "\nFirst embedding preview:"
#         )

#         print(
#             embeddings[0][:10]
#         )

#     # ========================================================
#     # TEST QUERY EMBEDDING
#     # ========================================================

#     query = (
#         "How many annual leave days "
#         "do employees get?"
#     )

#     print("\n")
#     print("#" * 70)
#     print("TESTING QUERY EMBEDDING")
#     print("#" * 70)

#     print(
#         f"Query: {query}"
#     )

#     query_embedding = embed_query(
#         query
#     )

#     print(
#         f"Query embedding dimension: "
#         f"{len(query_embedding)}"
#     )

#     print(
#         "\nFirst 10 query embedding values:"
#     )

#     print(
#         query_embedding[:10]
#     )

#     print(
#         "\nEmbedding test completed successfully."
#     )


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()
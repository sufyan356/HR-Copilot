from typing import List
from uuid import uuid4

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# TEXT SPLITTER
# ============================================================

def create_text_splitter():
    """
    Create the LangChain text splitter.

    chunk_size:
        Maximum approximate size of each chunk.

    chunk_overlap:
        Number of characters shared between adjacent chunks.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )


# ============================================================
# CHUNK DOCUMENTS
# ============================================================

def chunk_documents(
    documents: List[Document],
    doc_id: str,
) -> List[Document]:
    """
    Split documents into chunks.

    Each generated chunk receives:

        doc_id
        chunk_id

    Existing metadata is preserved:

        file_name
        file_type
        page_number
        row_number
    """

    splitter = create_text_splitter()

    chunks = []

    for document in documents:

        split_texts = splitter.split_text(
            document.page_content
        )

        for chunk_text in split_texts:

            # Copy the original metadata
            metadata = document.metadata.copy()

            # Add document-level ID
            metadata["doc_id"] = doc_id

            # Generate unique chunk ID
            metadata["chunk_id"] = str(uuid4())

            chunk = Document(
                page_content=chunk_text,
                metadata=metadata,
            )

            chunks.append(chunk)

    return chunks


# ============================================================
# PRINT CHUNKS
# ============================================================

def print_chunks(
    chunks: List[Document],
) -> None:
    """
    Print chunks and their metadata for testing.
    """

    print("\n" + "=" * 70)
    print("CREATED CHUNKS")
    print("=" * 70)

    print(
        f"Total chunks: {len(chunks)}"
    )

    for number, chunk in enumerate(
        chunks,
        start=1,
    ):

        metadata = chunk.metadata

        print("\n" + "-" * 70)

        print(
            f"Chunk #{number}"
        )

        print(
            f"doc_id:       "
            f"{metadata.get('doc_id')}"
        )

        print(
            f"chunk_id:     "
            f"{metadata.get('chunk_id')}"
        )

        print(
            f"file_name:    "
            f"{metadata.get('file_name')}"
        )

        print(
            f"file_type:    "
            f"{metadata.get('file_type')}"
        )

        print(
            f"page_number:  "
            f"{metadata.get('page_number')}"
        )

        print(
            f"row_number:   "
            f"{metadata.get('row_number')}"
        )

        print("\nChunk text:")

        print(chunk.page_content)


# ============================================================
# MAIN
# ============================================================

# def main():

#     from BACKEND.Rag.Indexing.loader import load_file
#     from BACKEND.Rag.Indexing.normalizer import normalize_documents

#     # ========================================================
#     # FILE PATHS
#     # ========================================================

#     excel_path = f"BACKEND\Data\hr-policy-data.xlsx"
#     pdf_path = f"BACKEND\Data\hr-policy.pdf"

#     # ========================================================
#     # TEST PDF
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING PDF CHUNKING")
#     print("#" * 70)

#     # Load PDF
#     pdf_documents = load_file(
#         pdf_path
#     )

#     # Normalize PDF
#     normalized_pdf = normalize_documents(
#         pdf_documents
#     )

#     # Generate ONE doc_id for the entire PDF
#     pdf_doc_id = str(uuid4())

#     print(
#         f"\nPDF doc_id: {pdf_doc_id}"
#     )

#     # Chunk PDF
#     pdf_chunks = chunk_documents(
#         normalized_pdf,
#         pdf_doc_id,
#     )

#     print_chunks(
#         pdf_chunks
#     )

#     # ========================================================
#     # TEST EXCEL
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING EXCEL CHUNKING")
#     print("#" * 70)

#     # Load Excel
#     excel_documents = load_file(
#         excel_path
#     )

#     # Normalize Excel
#     normalized_excel = normalize_documents(
#         excel_documents
#     )

#     # Generate ONE doc_id for the entire Excel file
#     excel_doc_id = str(uuid4())

#     print(
#         f"\nExcel doc_id: {excel_doc_id}"
#     )

#     # Chunk Excel
#     excel_chunks = chunk_documents(
#         normalized_excel,
#         excel_doc_id,
#     )

#     print_chunks(
#         excel_chunks
#     )

#     # ========================================================
#     # SUMMARY
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("CHUNKER TEST SUMMARY")
#     print("#" * 70)

#     print(
#         f"PDF pages:          "
#         f"{len(pdf_documents)}"
#     )

#     print(
#         f"PDF chunks:         "
#         f"{len(pdf_chunks)}"
#     )

#     print(
#         f"Excel rows:         "
#         f"{len(excel_documents)}"
#     )

#     print(
#         f"Excel chunks:       "
#         f"{len(excel_chunks)}"
#     )

#     print(
#         f"Total chunks:       "
#         f"{len(pdf_chunks) + len(excel_chunks)}"
#     )

#     print("\nChunker test completed successfully.")


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()
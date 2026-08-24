import re
from typing import List

from langchain_core.documents import Document


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning/end of lines
    text = re.sub(r" *\n *", "\n", text)

    # Replace 3+ consecutive newlines with 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# NORMALIZE DOCUMENTS
# ============================================================

def normalize_documents(
    documents: List[Document],
) -> List[Document]:
    """
    Normalize a list of LangChain Documents.

    The original metadata is preserved.
    """

    normalized_documents = []

    for document in documents:

        normalized_text = normalize_text(
            document.page_content
        )

        # Skip empty documents
        if not normalized_text:
            continue

        normalized_document = Document(
            page_content=normalized_text,
            metadata=document.metadata.copy(),
        )

        normalized_documents.append(
            normalized_document
        )

    return normalized_documents


# ============================================================
# PRINT NORMALIZED DOCUMENTS
# ============================================================

def print_documents(
    documents: List[Document],
) -> None:
    """
    Print normalized documents for testing.
    """

    print("\n" + "=" * 70)
    print("NORMALIZED DOCUMENTS")
    print("=" * 70)

    print(
        f"Total documents: {len(documents)}"
    )

    for number, document in enumerate(
        documents,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"Document #{number}"
        )

        print(
            f"File name:   "
            f"{document.metadata.get('file_name')}"
        )

        print(
            f"File type:   "
            f"{document.metadata.get('file_type')}"
        )

        print(
            f"Page number: "
            f"{document.metadata.get('page_number')}"
        )

        print(
            f"Row number:  "
            f"{document.metadata.get('row_number')}"
        )

        print("\nNormalized text:")

        print(document.page_content)


# ============================================================
# MAIN
# ============================================================

# def main():

#     from BACKEND.Rag.Indexing.loader import load_file

#     excel_path = f"BACKEND\Data\hr-policy-data.xlsx"
#     pdf_path = f"BACKEND\Data\hr-policy.pdf"

#     # ========================================================
#     # TEST PDF
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING PDF NORMALIZATION")
#     print("#" * 70)

#     pdf_documents = load_file(
#         pdf_path
#     )

#     normalized_pdf = normalize_documents(
#         pdf_documents
#     )

#     print_documents(
#         normalized_pdf
#     )

#     # ========================================================
#     # TEST EXCEL
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING EXCEL NORMALIZATION")
#     print("#" * 70)

#     excel_documents = load_file(
#         excel_path
#     )

#     normalized_excel = normalize_documents(
#         excel_documents
#     )

#     print_documents(
#         normalized_excel
#     )

#     # ========================================================
#     # SUMMARY
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("NORMALIZER TEST SUMMARY")
#     print("#" * 70)

#     print(
#         f"PDF documents before normalization: "
#         f"{len(pdf_documents)}"
#     )

#     print(
#         f"PDF documents after normalization:  "
#         f"{len(normalized_pdf)}"
#     )

#     print(
#         f"Excel rows before normalization:     "
#         f"{len(excel_documents)}"
#     )

#     print(
#         f"Excel rows after normalization:      "
#         f"{len(normalized_excel)}"
#     )

#     print("\nNormalizer test completed successfully.")


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()
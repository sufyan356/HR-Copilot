from pathlib import Path
from typing import List

import pandas as pd
from pypdf import PdfReader
from langchain_core.documents import Document


# ============================================================
# PDF LOADER
# ============================================================

def load_pdf(file_path: str) -> List[Document]:
    """
    Load PDF page by page using LangChain Document.

    Each PDF page becomes one LangChain Document.

    Metadata:
        file_name
        file_type
        page_number
        row_number
    """

    documents = []

    reader = PdfReader(file_path)

    file_name = Path(file_path).name

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        document = Document(
            page_content=text,

            metadata={
                "file_name": file_name,
                "file_type": "pdf",
                "page_number": page_number,
                "row_number": None,
            },
        )

        documents.append(document)

    return documents


# ============================================================
# EXCEL LOADER
# ============================================================

def load_excel(file_path: str) -> List[Document]:
    """
    Load Excel row by row using LangChain Document.

    Each Excel data row becomes one LangChain Document.

    Metadata:
        file_name
        file_type
        page_number -> None
        row_number
    """

    documents = []

    file_name = Path(file_path).name

    dataframe = pd.read_excel(file_path)

    for index, row in dataframe.iterrows():

        # Row 1 is assumed to contain headers.
        # Therefore first data row = Excel row 2.
        row_number = index + 2

        row_data = []

        for column, value in row.items():

            if pd.notna(value):

                row_data.append(
                    f"{column}: {value}"
                )

        text = "\n".join(row_data)

        document = Document(
            page_content=text,

            metadata={
                "file_name": file_name,
                "file_type": "xlsx",
                "page_number": None,
                "row_number": row_number,
            },
        )

        documents.append(document)

    return documents


# ============================================================
# GENERIC FILE LOADER
# ============================================================

def load_file(file_path: str) -> List[Document]:
    """
    Automatically select the correct loader
    based on the file extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":

        return load_pdf(file_path)

    elif extension in [".xlsx", ".xls"]:

        return load_excel(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


# ============================================================
# PRINT DOCUMENTS
# ============================================================

def print_documents(
    documents: List[Document]
) -> None:
    """
    Print LangChain Documents in a readable format.
    """

    print("\n" + "=" * 70)
    print("LOADED DOCUMENTS")
    print("=" * 70)

    print(
        f"Total documents: {len(documents)}"
    )

    for number, document in enumerate(
        documents,
        start=1
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

        print("\nPage content:")

        print(document.page_content)


# ============================================================
# MAIN
# ============================================================

# def main():

#     excel_path = f"BACKEND\Data\hr-policy-data.xlsx"
#     pdf_path = f"BACKEND\Data\hr-policy.pdf"

#     # ========================================================
#     # TEST PDF
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING PDF LOADER")
#     print("#" * 70)

#     pdf_documents = load_file(pdf_path)

#     print_documents(pdf_documents)

#     # ========================================================
#     # TEST EXCEL
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("TESTING EXCEL LOADER")
#     print("#" * 70)

#     excel_documents = load_file(excel_path)

#     print_documents(excel_documents)

#     # ========================================================
#     # SUMMARY
#     # ========================================================

#     print("\n")
#     print("#" * 70)
#     print("LOADER TEST SUMMARY")
#     print("#" * 70)

#     print(
#         f"PDF pages loaded:  "
#         f"{len(pdf_documents)}"
#     )

#     print(
#         f"Excel rows loaded: "
#         f"{len(excel_documents)}"
#     )

#     print(
#         f"Total documents:    "
#         f"{len(pdf_documents) + len(excel_documents)}"
#     )

#     print("\nLoader test completed successfully.")


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()
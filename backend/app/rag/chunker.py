from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(
    text: str,
    metadata: dict | None = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Document]:
    """Split *text* into overlapping chunks and attach metadata to each.

    Defaults match the project spec: 500-char chunks with 50-char overlap.
    Each returned Document carries:
      - page_content  : the chunk text
      - metadata      : merged base metadata + chunk_index + total_chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
        keep_separator=False,
    )

    base_meta = dict(metadata) if metadata else {}
    docs = splitter.create_documents([text], metadatas=[base_meta])

    total = len(docs)
    for i, doc in enumerate(docs):
        doc.metadata["chunk_index"] = i
        doc.metadata["total_chunks"] = total

    return docs

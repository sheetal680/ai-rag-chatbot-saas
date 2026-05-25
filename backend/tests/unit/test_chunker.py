from app.rag.chunker import chunk_text


def test_chunk_text_splits_long_text():
    text = "sentence. " * 200  # 2000 chars — well above chunk_size=500
    chunks = chunk_text(text)
    assert len(chunks) > 1
    # Allow a small buffer above chunk_size for the splitter's boundary logic
    assert all(len(c.page_content) <= 560 for c in chunks)


def test_chunk_text_short_text_single_chunk():
    text = "This is a short document."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].page_content == text

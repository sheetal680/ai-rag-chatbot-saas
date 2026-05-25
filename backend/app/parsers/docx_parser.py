import io

from docx import Document as DocxDocument


def parse_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file.

    Reads every paragraph and every table cell in document order.
    Returns a single string with double-newline section breaks.
    """
    doc = DocxDocument(io.BytesIO(file_bytes))
    parts: list[str] = []

    for block in doc.element.body:
        tag = block.tag.split("}")[-1]  # strip namespace

        if tag == "p":
            # Regular paragraph
            text = "".join(run.text for run in block.iterchildren() if run.tag.endswith("}r"))
            para_text = "".join(
                node.text or "" for node in block.iter() if node.tag.endswith("}t")
            )
            if para_text.strip():
                parts.append(para_text.strip())

        elif tag == "tbl":
            # Table — flatten rows into pipe-separated lines
            for row in block.iter():
                if row.tag.endswith("}tr"):
                    cells = [
                        "".join(n.text or "" for n in cell.iter() if n.tag.endswith("}t")).strip()
                        for cell in row
                        if cell.tag.endswith("}tc")
                    ]
                    line = " | ".join(c for c in cells if c)
                    if line:
                        parts.append(line)

    return "\n\n".join(parts)

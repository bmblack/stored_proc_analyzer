from docx import Document

def write_summary(docs, path="outputs/summary.docx"):
    document = Document()
    for doc in docs:
        document.add_heading(doc["name"], level=2)
        document.add_paragraph(doc["summary"])
    document.save(path)

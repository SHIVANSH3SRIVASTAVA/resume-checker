import pdfplumber, docx2txt, os
from .utils import split_sections

def extract_text_from_file(path: str) -> str:
    _, ext = os.path.splitext(path.lower())
    if ext == ".pdf":
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext in [".docx"]:
        return docx2txt.process(path) or ""
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def standardize(text: str) -> str:
    # normalize spaces and headers/footers heuristics
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # drop page numbers common pattern
    lines = [l for l in lines if not l.lower().startswith("page ")]
    return "\n".join(lines)

def parse_resume(text: str):
    std = standardize(text)
    sections = split_sections(std)
    return std, sections

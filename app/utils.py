import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\d{3,5}[-.\s]?\d{3,4}[-.\s]?\d{3,4})")
NAME_HINT_RE = re.compile(r"Name\s*:\s*(.+)", re.I)

def anonymize_pii(text: str) -> (str, dict):
    found = {}
    text, n = EMAIL_RE.subn("[EMAIL]", text)
    if n: found["emails"] = n
    text, n = PHONE_RE.subn("[PHONE]", text)
    if n: found["phones"] = n
    # light name redaction (heuristic)
    text = NAME_HINT_RE.sub("Name: [NAME]", text)
    return text, found

def split_sections(text: str):
    # very light heuristic section splitter
    anchors = ["education", "experience", "projects", "skills", "certifications", "summary", "objective"]
    sections = {}
    lower = text.lower()
    indices = []
    for a in anchors:
        i = lower.find(a)
        if i != -1:
            indices.append((i, a))
    indices.sort()
    for idx, (pos, name) in enumerate(indices):
        end = indices[idx + 1][0] if idx + 1 < len(indices) else len(text)
        sections[name] = text[pos:end].strip()
    return sections if sections else {"all": text}

def bullet_density(text: str):
    bullets = sum(1 for line in text.splitlines() if line.strip().startswith(("-", "•", "*")))
    lines = max(1, len(text.splitlines()))
    return bullets / lines

def verdict_from_score(score: float) -> str:
    return "High" if score >= 75 else ("Medium" if score >= 50 else "Low")

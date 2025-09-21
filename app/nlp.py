import spacy, json, os, re
from rapidfuzz import fuzz, process
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")
ONTOLOGY_PATH = os.getenv("SKILL_ONTOLOGY", "data/skill_ontology.json")
with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
    SKILL_ONTOLOGY = json.load(f)

def extract_entities(text: str) -> Dict[str, List[str]]:
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ in ("PERSON",)]
    orgs = [ent.text for ent in doc.ents if ent.label_ in ("ORG",)]
    locs = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
    return {"names": names, "orgs": orgs, "locs": locs}

def normalize_token(t: str) -> str:
    return re.sub(r"[^a-z0-9+#+.\- ]", " ", t.lower()).strip()

def extract_skills(text: str, seed: List[str] = None) -> List[str]:
    # heuristic: vocabulary from ontology + discovered n-grams that match closely
    base = set()
    for role in SKILL_ONTOLOGY.values():
        for sk in role.get("must_have", []) + role.get("good_to_have", []):
            base.add(normalize_token(sk))
    if seed:
        base |= set(normalize_token(s) for s in seed)
    candidates = set()
    words = [normalize_token(w) for w in text.split()]
    grams = set()
    for n in [1, 2, 3]:
        for i in range(len(words)-n+1):
            grams.add(" ".join(words[i:i+n]).strip())
    for g in grams:
        match, score, _ = process.extractOne(g, list(base)) if base else (None, 0, None)
        if score >= 90:
            candidates.add(match)
    return sorted(candidates)

def classify_career_stage(text: str) -> str:
    # very simple heuristic classifier
    exp_years = 0
    m = re.findall(r"(\d+)\+?\s*years", text.lower())
    if m:
        exp_years = max(int(x) for x in m)
    if "intern" in text.lower() or "fresher" in text.lower() or exp_years == 0:
        return "fresher"
    if exp_years <= 2: return "junior"
    if exp_years <= 5: return "mid"
    return "senior"

def parse_jd(raw_text: str) -> Dict:
    # Extract lists by cue words; optionally enriched by ontology
    lower = raw_text.lower()
    must = []
    good = []
    for role, info in SKILL_ONTOLOGY.items():
        for s in info.get("must_have", []):
            if s in lower: must.append(s)
        for s in info.get("good_to_have", []):
            if s in lower: good.append(s)
    must = sorted(set(must))
    good = sorted(set(good))
    return {"must_have": must, "good_to_have": good}

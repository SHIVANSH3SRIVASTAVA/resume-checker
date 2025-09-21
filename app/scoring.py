from rapidfuzz import fuzz
from typing import Dict, List
from .semantic import cosine
from .utils import verdict_from_score

def hard_match_scores(resume_text: str, jd_must: List[str], jd_good: List[str]) -> Dict:
    exact_hits = []
    fuzzy_hits = []
    missing = []
    for skill in jd_must:
        if skill in resume_text.lower():
            exact_hits.append(skill)
        else:
            score = fuzz.partial_ratio(skill, resume_text.lower())
            if score >= 85:
                fuzzy_hits.append({"skill": skill, "score": score})
            else:
                missing.append(skill)
    good_hits = []
    for skill in jd_good:
        if skill in resume_text.lower():
            good_hits.append(skill)
    return {
        "exact_hits": exact_hits,
        "fuzzy_hits": fuzzy_hits,
        "good_hits": good_hits,
        "missing_must": missing
    }

def combine_score(hard: Dict, soft_sim: float, ats: Dict) -> Dict:
    # weights tuned for clarity; adjust during demo via Streamlit slider
    w_hard = 0.55
    w_soft = 0.35
    w_ats = 0.10
    hard_cov = 0.0
    denom = len(hard["exact_hits"]) + len(hard["fuzzy_hits"]) + len(hard["missing_must"])
    if denom > 0:
        hard_cov = (len(hard["exact_hits"]) + 0.6*len(hard["fuzzy_hits"])) / denom
    ats_norm = min(1.0, max(0.0, ats.get("score", 0)/100.0))
    overall = 100.0 * (w_hard*hard_cov + w_soft*soft_sim + w_ats*ats_norm)
    return {"overall": overall, "verdict": verdict_from_score(overall),
            "weights": {"hard": w_hard, "soft": w_soft, "ats": w_ats},
            "components": {"hard_coverage": hard_cov, "soft_similarity": soft_sim, "ats_norm": ats_norm}}

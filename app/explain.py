from typing import Dict, List

def evidence_cards(resume_text: str, skills: List[str]) -> List[Dict]:
    cards = []
    lower = resume_text.lower()
    lines = resume_text.splitlines()
    for s in skills:
        indices = [i for i,l in enumerate(lines) if s in l.lower()]
        snippet = ""
        if indices:
            i = indices[0]
            snippet = "\n".join(lines[max(0,i-1):min(len(lines), i+2)])
        cards.append({"skill": s, "found": bool(indices), "snippet": snippet})
    return cards

def shap_like(weights: Dict, components: Dict) -> List[Dict]:
    # simple feature importance style breakdown for display
    contribs = []
    for k, w in weights.items():
        comp = components["hard_coverage"] if k=="hard" else (components["soft_similarity"] if k=="soft" else components["ats_norm"])
        contribs.append({"component": k, "weight": w, "value": comp, "contribution": w*comp*100.0})
    return contribs

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Resume, JobDescription, Evaluation
from ..schemas import EvaluateRequest, EvaluationOut
from ..scoring import hard_match_scores, combine_score
from ..semantic import embed, cosine
from ..utils import anonymize_pii, bullet_density
from ..explain import evidence_cards, shap_like
from ..feedback import generate_feedback
from typing import List
from ..schemas import EvaluationOut 
router = APIRouter(prefix="/evaluate", tags=["evaluate"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ats_report(resume_text: str, jd_must) -> dict:
    bd = bullet_density(resume_text)
    has_secs = any(h in resume_text.lower() for h in ["experience", "education", "skills", "projects"])
    kc_hits = sum(1 for s in jd_must if s in resume_text.lower())
    kc = kc_hits / max(1, len(jd_must))
    score = 100 * (0.4*kc + 0.4*min(1.0, max(0.0, bd/0.4)) + 0.2*(1 if has_secs else 0))
    return {"bullet_density": bd, "bullet_density_ok": 0.15 <= bd <= 0.5, "has_sections": has_secs, "keyword_coverage": kc, "score": score}

@router.post("/", response_model=EvaluationOut)
async def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    resume = db.get(Resume, req.resume_id)
    jd = db.get(JobDescription, req.jd_id)
    if not resume or not jd:
        raise HTTPException(404, "Resume or JD not found")

    rtext = resume.anonymized_text if req.bias_anonymize else resume.raw_text
    hard = hard_match_scores(rtext, jd.must_have or [], jd.good_to_have or [])
    # soft similarity
    r_emb = resume.embedding
    j_emb = embed(jd.raw_text)
    soft_sim = cosine(r_emb, j_emb)
    ats = ats_report(rtext, jd.must_have or [])
    combined = combine_score(hard, soft_sim, ats)

    missing_elements = {
        "skills": hard["missing_must"],
        "certifications": [],  # could be inferred with regex list
        "projects": []  # can be inferred if no 'projects' section present
    }
    expl_cards = evidence_cards(rtext, (jd.must_have or []) + (jd.good_to_have or []))
    shap = shap_like(combined["weights"], combined["components"])
    feedback = generate_feedback(resume.career_stage, hard["missing_must"], ats)

    ev = Evaluation(
        resume_id=resume.id,
        jd_id=jd.id,
        relevance_score=combined["overall"],
        verdict=combined["verdict"],
        hard_match=hard,
        soft_match={"similarity": soft_sim},
        missing_elements=missing_elements,
        feedback=feedback,
        explainability={"evidence": expl_cards, "contributions": shap},
        ats_report=ats,
        bias_anonymized=req.bias_anonymize
    )
    db.add(ev); db.commit(); db.refresh(ev)
    return ev
@router.get("/dashboard")
def get_evaluations(
    job_title: str = "",
    min_score: float = 0.0,
    location: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Evaluation).join(Resume).join(JobDescription)

    if job_title:
        query = query.filter(JobDescription.title.ilike(f"%{job_title}%"))
    if location:
        query = query.filter(Resume.location.ilike(f"%{location}%"))
    query = query.filter(Evaluation.relevance_score >= min_score)

    results = query.order_by(Evaluation.relevance_score.desc()).limit(50).all()
    return results


 # Make sure this is imported

@router.get("/dashboard", response_model=List[EvaluationOut])
def get_evaluations(
    job_title: str = "",
    min_score: float = 0.0,
    location: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Evaluation).join(Resume).join(JobDescription)

    if job_title:
        query = query.filter(JobDescription.title.ilike(f"%{job_title}%"))
    if location:
        query = query.filter(Resume.location.ilike(f"%{location}%"))
    query = query.filter(Evaluation.relevance_score >= min_score)

    results = query.order_by(Evaluation.relevance_score.desc()).limit(50).all()
    return results

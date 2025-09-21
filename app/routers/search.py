from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Evaluation, Resume, JobDescription

router = APIRouter(prefix="/search", tags=["search"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/shortlist")
def shortlist(jd_id: int, min_score: float = 60.0, location: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    q = select(Evaluation, Resume).join(Resume).where(Evaluation.jd_id == jd_id, Evaluation.relevance_score >= min_score).order_by(Evaluation.relevance_score.desc()).limit(limit)
    rows = db.execute(q).all()
    results = []
    for ev, res in rows:
        if location and res.location and location.lower() not in res.location.lower():
            continue
        results.append({
            "evaluation_id": ev.id,
            "resume_id": res.id,
            "score": ev.relevance_score,
            "verdict": ev.verdict,
            "career_stage": res.career_stage
        })
    return results

@router.get("/matrix")
def matrix(resume_id: int, db: Session = Depends(get_db)):
    # match a resume against all JDs (multi-JD matrix)
    jds = db.query(JobDescription).all()
    evs = db.query(Evaluation).filter(Evaluation.resume_id == resume_id).all()
    ev_map = {(e.jd_id): e for e in evs}
    out = []
    for jd in jds:
        e = ev_map.get(jd.id)
        out.append({
            "jd_id": jd.id, "jd_title": jd.title, "company": jd.company,
            "score": e.relevance_score if e else None,
            "verdict": e.verdict if e else None
        })
    return out

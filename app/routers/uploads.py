import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Resume, JobDescription
from ..schemas import ResumeOut, JDOut, JDCreate
from ..nlp import parse_jd, classify_career_stage
from ..parsing import extract_text_from_file, parse_resume
from ..semantic import embed
from ..utils import anonymize_pii

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/resume", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            f.write(content)

        raw_text = extract_text_from_file(path)
        std_text, sections = parse_resume(raw_text)
        anonymized_text, _ = anonymize_pii(std_text)
        career_stage = classify_career_stage(std_text)
        embedding = embed(anonymized_text)

        r = Resume(
            raw_text=std_text,
            anonymized_text=anonymized_text,
            sections=sections,
            career_stage=career_stage,
            embedding=embedding
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        print(f"✅ Resume saved: {r.id}")
        return r
    except Exception as e:
        print(f"❌ Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}")

@router.post("/jd", response_model=JDOut)
async def upload_jd(jd: JDCreate, db: Session = Depends(get_db)):
    try:
        derived = parse_jd(jd.raw_text)
        j = JobDescription(
            title=jd.title,
            company=jd.company,
            location=jd.location,
            raw_text=jd.raw_text,
            must_have=jd.must_have or derived["must_have"],
            good_to_have=jd.good_to_have or derived["good_to_have"]
        )
        db.add(j)
        db.commit()
        db.refresh(j)
        print(f"✅ JD saved: {j.id}")
        return j
    except Exception as e:
        print(f"❌ JD upload error: {e}")
        raise HTTPException(status_code=500, detail=f"JD upload failed: {str(e)}")

@router.post("/jd-file", response_model=JDOut)
async def upload_jd_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            f.write(content)

        raw_text = extract_text_from_file(path)
        derived = parse_jd(raw_text)

        j = JobDescription(
            title=file.filename,
            company="",
            location="",
            raw_text=raw_text,
            must_have=derived["must_have"],
            good_to_have=derived["good_to_have"]
        )
        db.add(j)
        db.commit()
        db.refresh(j)
        print(f"✅ JD file saved: {j.id}")
        return j
    except Exception as e:
        print(f"❌ JD file upload error: {e}")
        raise HTTPException(status_code=500, detail=f"JD file upload failed: {str(e)}")

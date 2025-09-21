from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class JDCreate(BaseModel):
    title: str
    company: str
    location: str = ""
    raw_text: str
    must_have: Optional[List[str]] = None
    good_to_have: Optional[List[str]] = None

class JDOut(JDCreate):
    id: int
    class Config: from_attributes = True

class ResumeCreate(BaseModel):
    raw_text: str
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""

class ResumeOut(ResumeCreate):
    id: int
    anonymized_text: str
    sections: Dict[str, Any] = {}
    career_stage: str = "unknown"
    class Config:
        from_attributes = True

class EvaluateRequest(BaseModel):
    resume_id: int
    jd_id: int
    bias_anonymize: bool = True

class EvaluationOut(BaseModel):
    id: int
    relevance_score: float
    verdict: str
    missing_elements: Dict[str, List[str]]
    feedback: str
    hard_match: Dict[str, Any]
    soft_match: Dict[str, Any]
    explainability: Dict[str, Any]
    ats_report: Dict[str, Any]
    bias_anonymized: bool
    resume: ResumeOut
    jd: JDOut

    class Config:
        from_attributes = True

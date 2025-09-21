from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    raw_text = Column(Text)
    must_have = Column(JSON, default=[])
    good_to_have = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="jd")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, index=True, default="")
    email = Column(String, index=True, default="")
    phone = Column(String, index=True, default="")
    location = Column(String, index=True, default="")
    raw_text = Column(Text)
    sections = Column(JSON, default={})
    anonymized_text = Column(Text)
    embedding = Column(JSON)  # store list[float]
    career_stage = Column(String, default="unknown")  # fresher, junior, mid, senior
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="resume")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"))
    relevance_score = Column(Float)
    verdict = Column(String)  # High / Medium / Low
    hard_match = Column(JSON, default={})
    soft_match = Column(JSON, default={})
    missing_elements = Column(JSON, default={"skills": [], "certifications": [], "projects": []})
    feedback = Column(Text)
    explainability = Column(JSON, default={})
    ats_report = Column(JSON, default={})
    bias_anonymized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="evaluations")
    jd = relationship("JobDescription", back_populates="evaluations")

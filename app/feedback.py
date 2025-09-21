from typing import Dict, List

CAREER_TIPS = {
    "fresher": [
        "Add 2-3 quantified academic or personal projects aligned with the JD.",
        "Include a concise skills section grouped by category (Languages, Tools, Cloud)."
    ],
    "junior": [
        "Demonstrate impact with metrics (throughput, latency, accuracy improvements).",
        "Add 1-2 production incidents or ownership moments."
    ],
    "mid": [
        "Show cross-functional collaboration and system design decisions.",
        "List tech leadership moments: reviews, mentoring, roadmap inputs."
    ],
    "senior": [
        "Highlight architecture trade-offs and org-level influence.",
        "Quantify cost, reliability, and velocity improvements."
    ]
}

def generate_feedback(career_stage: str, missing_skills: List[str], ats_report: Dict) -> str:
    tips = CAREER_TIPS.get(career_stage, CAREER_TIPS["junior"])
    gaps = ""
    if missing_skills:
        gaps = f"Top missing skills to add or demonstrate: {', '.join(missing_skills[:6])}."
    ats_tips = []
    if ats_report.get("bullet_density_ok") is False:
        ats_tips.append("Improve bullet structure; target 20–40% of lines as bullets.")
    if ats_report.get("has_sections") is False:
        ats_tips.append("Add clear sections: Summary, Skills, Experience, Projects, Education.")
    if ats_report.get("keyword_coverage", 0) < 0.5:
        ats_tips.append("Increase JD keyword coverage in your bullet points.")
    return (
        f"{gaps}\n"
        f"Career-stage suggestions: " + " ".join(tips) + "\n"
        f"ATS tips: " + (" ".join(ats_tips) if ats_tips else "Good ATS hygiene overall.")
    )

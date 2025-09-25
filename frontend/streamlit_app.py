import streamlit as st
import requests
import mimetypes
import matplotlib.pyplot as plt

# Backend URL
BACKEND = st.secrets.get("BACKEND_URL", "https://ae605454-f22b-4bf6-9b47-83e854618ccc-00-2hzu7b2t5e1c0.janeway.replit.dev")

st.set_page_config(page_title="Innomatics Resume Checker", layout="wide")
st.title("Automated Resume Relevance Check System")

def safe_post(url, **kwargs):
    try:
        r = requests.post(url, **kwargs)
        if r.ok:
            try:
                return r.json(), None
            except ValueError:
                return None, f"Invalid JSON from backend:\n{r.text}"
        else:
            return None, f"Error {r.status_code}:\n{r.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Upload Resume", "Evaluate (Simulated)", "Matrix (Simulated)",
    "What-if Simulator (Simulated)", "Placement Dashboard (Simulated)"
])

# -------------------------
# Tab 1: Resume Upload
# -------------------------
with tab1:
    st.subheader("📄 Upload Resume")
    f = st.file_uploader("Choose Resume file", type=["pdf", "docx", "txt"], key="resume_file")
    if f and st.button("Analyze Resume"):
        mime_type = f.type or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        files = {"file": (f.name, f.getvalue(), mime_type)}
        data, err = safe_post(f"{BACKEND}/analyze/resume", files=files)
        if err:
            st.error(f"❌ Resume upload failed: {err}")
        else:
            st.success("✅ Resume analyzed successfully!")
            st.markdown(f"### 📄 Filename: `{data.get('filename', '—')}`")
            st.subheader("📊 Skills Analysis")
            st.json(data.get("skills_analysis", {}))
            st.subheader("📈 Experience Analysis")
            st.json(data.get("experience_analysis", {}))
            st.subheader("📋 ATS Report")
            st.json(data.get("ats_analysis", {}))
            st.subheader("📇 Contact Info")
            st.json(data.get("contact_info", {}))
            st.subheader("🎓 Education Info")
            st.json(data.get("education_info", {}))
            st.subheader("🧠 Overall Score")
            st.json(data.get("overall_score", {}))
            st.subheader("📜 Extracted Resume Text")
            st.text_area("Resume Text", value=data.get("extracted_text", ""), height=300)

# -------------------------
# Tab 2: Evaluate (Simulated)
# -------------------------
with tab2:
    st.subheader("📊 Evaluate Resume vs JD (Simulated)")
    st.info("This feature is not yet connected to the backend. Showing simulated output.")
    st.metric("Relevance Score", "72.5")
    st.metric("Verdict", "Strong Match")
    st.metric("ATS Score", "88")

    st.subheader("Explainability Breakdown")
    st.write("• Skills: 0.45\n• Experience: 0.35\n• ATS: 0.20")

    st.subheader("Skill Evidence")
    st.code("Python, SQL, Machine Learning — Found")

    st.subheader("Feedback")
    st.write("Consider adding more quantifiable achievements and certifications.")

# -------------------------
# Tab 3: Matrix (Simulated)
# -------------------------
with tab3:
    st.subheader("📐 Multi-JD Matrix (Simulated)")
    st.info("This feature is not yet connected to the backend. Showing simulated matrix.")
    st.dataframe({
        "JD Title": ["Data Scientist", "ML Engineer", "AI Analyst"],
        "Relevance Score": [72.5, 65.0, 80.2],
        "Verdict": ["Strong Match", "Moderate Match", "Excellent Match"]
    })

# -------------------------
# Tab 4: What-if Simulator (Simulated)
# -------------------------
with tab4:
    st.subheader("🔮 What-if Skill Simulator (Simulated)")
    st.caption("Add hypothetical skills to see how the score could change.")
    add_skills = st.text_input("Pretend I have these skills (comma-separated)")
    weights_hard = st.slider("Weight: Hard", 0.0, 1.0, 0.55, 0.05)
    weights_soft = st.slider("Weight: Soft", 0.0, 1.0, 0.35, 0.05)
    weights_ats = st.slider("Weight: ATS", 0.0, 1.0, 0.10, 0.05)

    if st.button("Simulate"):
        st.metric("Baseline Score", "72.5")
        st.metric("Simulated Score", "84.3")

        st.subheader("Score Contribution Breakdown")
        fig, ax = plt.subplots()
        ax.pie([55, 35, 10], labels=["Hard", "Soft", "ATS"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

# -------------------------
# Tab 5: Placement Dashboard (Simulated)
# -------------------------
with tab5:
    st.subheader("🎯 Placement Team Dashboard (Simulated)")
    job_filter = st.text_input("Filter by Job Title")
    loc_filter = st.text_input("Filter by Location")
    score_filter = st.slider("Minimum Score", 0.0, 100.0, 60.0)

    if st.button("Search Matches"):
        st.success("Found 3 matching resumes")
        st.markdown("### 🧑 Resume ID: `101` — Score: `72.5`")
        st.write("**Verdict:** Strong Match")
        st.write("**Job Title:** Data Scientist")
        st.write("**Location:** Hyderabad")
        st.write("**Missing Skills:** NLP, Docker")
        st.markdown("---")
        st.markdown("### 🧑 Resume ID: `102` — Score: `65.0`")
        st.write("**Verdict:** Moderate Match")
        st.write("**Job Title:** ML Engineer")
        st.write("**Location:** Bangalore")
        st.write("**Missing Skills:** Kubernetes, PyTorch")
        st.markdown("---")

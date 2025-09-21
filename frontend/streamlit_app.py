import streamlit as st
import requests
import mimetypes
import matplotlib.pyplot as plt
# Backend URL
BACKEND = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")

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

tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Evaluate", "Matrix", "What-if Simulator"])

# -------------------------
# Tab 1: Upload
# -------------------------
with tab1:
    st.subheader("📝 Manual JD Entry")
    jd_title = st.text_input("Job Title")
    jd_company = st.text_input("Company")
    jd_location = st.text_input("Location")
    jd_text = st.text_area("JD Raw Text", height=200)
    colA, colB = st.columns(2)
    with colA:
        must = st.text_area("Must-have skills (comma-separated)")
    with colB:
        good = st.text_area("Good-to-have skills (comma-separated)")

    if st.button("Save JD"):
        payload = {
            "title": jd_title,
            "company": jd_company,
            "location": jd_location,
            "raw_text": jd_text,
            "must_have": [x.strip().lower() for x in must.split(",")] if must.strip() else None,
            "good_to_have": [x.strip().lower() for x in good.split(",")] if good.strip() else None
        }
        data, err = safe_post(f"{BACKEND}/upload/jd", json=payload)
        if err:
            st.error(err)
        else:
            st.success("JD saved successfully!")
            st.json(data)

    st.subheader("📑 Upload JD from File")
    jd_file = st.file_uploader("Choose JD file", type=None, key="jd_file")
    if jd_file and st.button("Save JD from file"):
        mime_type = jd_file.type or mimetypes.guess_type(jd_file.name)[0] or "application/octet-stream"
        files = {"file": (jd_file.name, jd_file.getvalue(), mime_type)}
        data, err = safe_post(f"{BACKEND}/upload/jd-file", files=files)
        if err:
            st.error(f"❌ JD upload failed: {err}")
        else:
            st.success("✅ JD uploaded successfully!")
            st.markdown(f"### 📄 {data.get('title', 'Untitled')}")
            st.write(f"**Company:** {data.get('company', '—')}")
            st.write(f"**Location:** {data.get('location', '—')}")
            st.markdown("**Must-have Skills:**")
            for skill in data.get("must_have", []):
                st.markdown(f"- ✅ `{skill}`")
            st.markdown("**Good-to-have Skills:**")
            for skill in data.get("good_to_have", []):
                st.markdown(f"- 🌟 `{skill}`")
            with st.expander("🔍 Raw JD Text"):
                st.write(data.get("raw_text", "—"))

    st.subheader("📄 Upload Resume")
    f = st.file_uploader("Choose Resume file", type=None, key="resume_file")
    if f and st.button("Save Resume"):
        mime_type = f.type or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        files = {"file": (f.name, f.getvalue(), mime_type)}
        data, err = safe_post(f"{BACKEND}/upload/resume", files=files)
        if err:
            st.error(f"❌ Resume upload failed: {err}")
        else:
            st.success("✅ Resume uploaded successfully!")
            st.markdown(f"### 📄 Resume ID: `{data.get('id', '—')}`")
            st.write(f"**Career Stage:** `{data.get('career_stage', '—')}`")
            st.markdown("**Sections Extracted:**")
            for section in data.get("sections", []):
                st.markdown(f"- 📌 `{section}`")
            if "anonymized_text" in data:
                with st.expander("🔍 Anonymized Resume Text"):
                    st.write(data["anonymized_text"])
                st.download_button("⬇️ Download Anonymized Resume", data["anonymized_text"], file_name="anonymized_resume.txt")
            else:
                st.warning("⚠️ Anonymized text not returned.")
                st.json(data)

# -------------------------
# Tab 2: Evaluate
# -------------------------
with tab2:
    st.subheader("📊 Evaluate Resume vs JD")
    rid = st.number_input("Resume ID", min_value=1, step=1)
    jid = st.number_input("JD ID", min_value=1, step=1)
    bias = st.checkbox("Bias-aware anonymization", value=True)
    if st.button("Run Evaluation"):
        data, err = safe_post(f"{BACKEND}/evaluate/", json={
            "resume_id": int(rid),
            "jd_id": int(jid),
            "bias_anonymize": bias
        })
        if err:
            st.error(err)
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Relevance Score", f"{data['relevance_score']:.1f}")
            c2.metric("Verdict", data["verdict"])
            c3.metric("ATS Score", f"{data['ats_report']['score']:.0f}")

            st.subheader("Explainability Breakdown")
            for item in data["explainability"]["contributions"]:
                st.markdown(f"**{item['component'].capitalize()}**")
                st.write(f"Weight: `{item['weight']}`")
                st.write(f"Value: `{item['value']}`")
                st.write(f"Contribution: `{item['contribution']:.2f}`")
                st.markdown("---")

            st.subheader("Skill Evidence")
            for card in data["explainability"]["evidence"]:
                col1, col2 = st.columns([1, 3])
                col1.write(f"• `{card['skill']}` — {'✅ Found' if card['found'] else '❌ Missing'}")
                col2.code(card["snippet"] or "—", language="text")

            st.subheader("Feedback")
            st.write(data["feedback"])

            st.subheader("ATS Report")
            ats = data["ats_report"]
            st.write(f"**Score:** `{ats['score']:.1f}`")
            st.write(f"**Keyword Coverage:** `{ats['keyword_coverage']}`")
            st.write(f"**Bullet Density:** `{ats['bullet_density']:.2f}` — {'✅ OK' if ats['bullet_density_ok'] else '❌ Too sparse'}")
            st.write(f"**Has Sections:** {'✅ Yes' if ats['has_sections'] else '❌ No'}")

            st.subheader("Missing Elements")
            missing = data["missing_elements"]
            st.markdown("**Skills:**")
            for skill in missing.get("skills", []):
                st.markdown(f"- ❌ `{skill}`")
            st.markdown("**Certifications:**")
            for cert in missing.get("certifications", []):
                st.markdown(f"- ❌ `{cert}`")
            st.markdown("**Projects:**")
            for proj in missing.get("projects", []):
                st.markdown(f"- ❌ `{proj}`")

# (Tab 3 and Tab 4 remain unchanged unless you'd like me to enhance those too)

# -------------------------
# Tab 3: Multi-JD Matrix
# -------------------------
with tab3:
    st.subheader("📐 Multi-JD Matrix")
    rid2 = st.number_input("Resume ID for Matrix", min_value=1, step=1, key="rid2")
    if st.button("Build Matrix"):
        try:
            r = requests.get(f"{BACKEND}/search/matrix", params={"resume_id": int(rid2)})
            if r.status_code == 200:
                st.dataframe(r.json(), use_container_width=True)
            else:
                st.error(f"Error {r.status_code}:\n{r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")

# -------------------------
# Tab 4: What-if Simulator
# -------------------------
with tab4:
    st.subheader("🔮 What-if Skill Simulator")
    st.caption("Add hypothetical skills to see how the score could change.")
    rid3 = st.number_input("Resume ID", min_value=1, step=1, key="rid3")
    jid3 = st.number_input("JD ID", min_value=1, step=1, key="jid3")
    add_skills = st.text_input("Pretend I have these skills (comma-separated)")
    weights_hard = st.slider("Weight: Hard", 0.0, 1.0, 0.55, 0.05)
    weights_soft = st.slider("Weight: Soft", 0.0, 1.0, 0.35, 0.05)
    weights_ats = st.slider("Weight: ATS", 0.0, 1.0, 0.10, 0.05)

    if st.button("Simulate"):
        base, err = safe_post(f"{BACKEND}/evaluate/", json={
            "resume_id": int(rid3),
            "jd_id": int(jid3),
            "bias_anonymize": True
        })
        if err:
            st.error(err)
        else:
            must = set(base["hard_match"].get("missing_must", []))
            hypothetical = set([s.strip().lower() for s in add_skills.split(",") if s.strip()])
            new_missing = [s for s in must if s not in hypothetical]

            denom = len(must) + len(base["hard_match"].get("exact_hits", [])) + len(base["hard_match"].get("fuzzy_hits", []))
            hard_cov = 0.0 if denom == 0 else (
                len(base["hard_match"].get("exact_hits", [])) +
                len(base["hard_match"].get("fuzzy_hits", [])) * 0.6 +
                len(hypothetical & must)
            ) / denom

            soft_sim = base["soft_match"].get("similarity", 0.0)
            ats_norm = min(1.0, base["ats_report"].get("score", 0.0) / 100.0)
            total = 100.0 * (weights_hard * hard_cov + weights_soft * soft_sim + weights_ats * ats_norm)

            # Score metrics
            c1, c2 = st.columns(2)
            c1.metric("Baseline Score", f"{base['relevance_score']:.1f}")
            c2.metric("Simulated Score", f"{total:.1f}")

            # Pie chart
            st.subheader("Score Contribution Breakdown")
            labels = []
            sizes = []
            colors = ["#4CAF50", "#2196F3", "#FFC107"]
            for item in base["explainability"]["contributions"]:
                labels.append(item["component"].capitalize())
                sizes.append(item["contribution"])
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
            ax.axis("equal")
            st.pyplot(fig)

            # Skill evidence
            st.subheader("Skill Evidence")
            for card in base["explainability"]["evidence"]:
                col1, col2 = st.columns([1, 3])
                col1.write(f"• `{card['skill']}` — {'✅ Found' if card['found'] else '❌ Missing'}")
                col2.code(card["snippet"] or "—", language="text")

            # Feedback
            st.subheader("Feedback")
            st.write(base["feedback"])

            # ATS Report
            st.subheader("ATS Report")
            ats = base["ats_report"]
            st.write(f"**Score:** `{ats['score']:.1f}`")
            st.write(f"**Keyword Coverage:** `{ats['keyword_coverage']}`")
            st.write(f"**Bullet Density:** `{ats['bullet_density']:.2f}` — {'✅ OK' if ats['bullet_density_ok'] else '❌ Too sparse'}")
            st.write(f"**Has Sections:** {'✅ Yes' if ats['has_sections'] else '❌ No'}")

            # Missing Elements
            st.subheader("New Missing Must-Have Skills")
            for skill in new_missing:
                st.markdown(f"- ❌ `{skill}`")
            st.caption("Use this to prioritize your upskilling before applying.")


# -------------------------
# Tab 5: Placcement Simulator
# -------------------------
tab5 = st.tabs(["Placement Dashboard"])[0]

with tab5:
    st.subheader("🎯 Placement Team Dashboard")
    job_filter = st.text_input("Filter by Job Title")
    loc_filter = st.text_input("Filter by Location")
    score_filter = st.slider("Minimum Score", 0.0, 100.0, 60.0)

    if st.button("Search Matches"):
        params = {
            "job_title": job_filter,
            "location": loc_filter,
            "min_score": score_filter
        }
        r = requests.get(f"{BACKEND}/evaluate/dashboard", params=params)
        if r.ok:
            results = r.json()
            st.success(f"Found {len(results)} matching resumes")
            for eval in results:
                st.markdown(f"### 🧑 Resume ID: `{eval['resume']['id']}` — Score: `{eval['relevance_score']:.1f}`")
                st.write(f"**Verdict:** {eval['verdict']}")
                st.write(f"**Job Title:** {eval['jd']['title']}")
                st.write(f"**Location:** {eval['resume']['location']}")
                st.write(f"**Missing Skills:** {', '.join(eval['missing_elements']['skills'])}")
                st.markdown("---")
        else:
            st.error("Failed to fetch results")

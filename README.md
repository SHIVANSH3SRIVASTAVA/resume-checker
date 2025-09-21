# 🧠 Resume Checker

**Hackathon Project – Code4EdTech Submission**  
A smart resume evaluation tool built with **FastAPI**, **PostgreSQL**, and **Streamlit**, designed to help candidates tailor their resumes to job descriptions and improve their chances of landing interviews.

---

## 🚀 Key Features

- 📄 Upload resume and job description (PDF, DOCX, TXT)
- 🧠 Intelligent scoring based on keyword and semantic match
- 🕵️ Bias anonymization (removes name, gender, age indicators)
- 📊 Streamlit dashboard with match score and suggestions
- 🔐 Robust error handling for file formats and backend failures
- ⚙️ Automated setup scripts for easy deployment and testing

---

## 🧱 Tech Stack

- **Backend**: FastAPI, Pydantic, Uvicorn  
- **Database**: PostgreSQL, SQLAlchemy  
- **Frontend**: Streamlit  
- **Deployment**: Streamlit Cloud / HuggingFace Spaces  
- **Dev Tools**: GitHub Desktop, PowerShell, VS Code

---

## 📦 Project Structure

```
resume-checker/
├── app/                  # FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   └── utils/
├── frontend/             # Streamlit frontend
│   └── streamlit_app.py
├── init_db.py            # DB initialization script
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
```

---

## 🧪 Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/resume-checker.git
cd resume-checker
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize PostgreSQL Database

Ensure PostgreSQL is running locally, then:

```bash
python init_db.py
```

### 5. Start Backend Server

```bash
uvicorn app.main:app --reload
```

### 6. Launch Frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

## 🌐 Live Demo & Submission Links

- 🔗 **Web App**: [https://resume-checker.streamlit.app](https://resume-checker.streamlit.app)  
- 🎥 **Video Walkthrough**: [https://youtu.be/YOUR_VIDEO_ID](https://youtu.be/YOUR_VIDEO_ID)  
- 📁 **GitHub Repo**: [https://github.com/YOUR_USERNAME/resume-checker](https://github.com/YOUR_USERNAME/resume-checker)

---

## 🎯 Use Cases

- Students preparing for placements  
- Job seekers tailoring resumes to specific roles  
- Recruiters evaluating resume-job fit  
- Career counselors offering resume feedback

---

## 🛡️ Error Handling Highlights

- ✅ Detects and handles empty or malformed files  
- ✅ Validates file types and content  
- ✅ Displays user-friendly error messages  
- ✅ Logs backend exceptions for debugging

---

## 📈 Future Enhancements

- 🔍 NLP-based semantic scoring (spaCy, BERT)  
- 🧾 Resume formatting suggestions  
- 🧠 AI-generated resume edits  
- 📤 Email integration for feedback delivery

---

## 🤝 Contributor

**Shivansh** – Developer, UX Designer, Backend Architect  
- GitHub: [https://github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)  
- LinkedIn: [https://linkedin.com/in/YOUR_PROFILE](https://linkedin.com/in/YOUR_PROFILE)

---

## 📜 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 🙌 Acknowledgments

- Code4EdTech Hackathon organizers  
- Streamlit and FastAPI communities  
- PostgreSQL documentation and tutorials

---

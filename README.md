# 📄 Minimal ATS Resume Scanner & Job Matcher

A fast, lightweight, and modern **ATS Resume Screening Platform** built with **Python (Flask), Google Gemini AI, and Vanilla HTML/CSS/JS**. 

Styled with a minimal **Slate Gray (`#708090`) & Warm Cream (`#FAF3E0`)** aesthetic.

---

## ✨ Features

1. **General ATS Resume Score:**
   - Upload any `.pdf`, `.docx`, or `.txt` resume.
   - Extracts keywords, checks formatting hierarchy, and calculates an **ATS Score (0–100)**.
   - Highlights detected skills, resume strengths, and actionable improvements.

2. **Job-Targeted ATS Match:**
   - Enter a **Target Job Title** and paste the **Job Description**.
   - Upload your resume to calculate a **Targeted Match Score (0–100)**.
   - Identifies **Matched Keywords** (green tags), **Missing Critical Keywords** (red tags), and tips to pass ATS filters for that specific role.

3. **No Database Required:**
   - Processes files in-memory on demand without database setup or migrations.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask
- **AI / LLM:** Google Gemini API (`google-generativeai`)
- **Document Parsing:** `pdfplumber`, `PyPDF2`, `python-docx`
- **Frontend:** HTML5, Vanilla CSS3 (Slate Gray & Warm Cream), Vanilla JavaScript

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/vivek9369/Resume_Parser.git
cd Resume_Parser
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```
*(Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey))*

### 4. Run the app
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 📁 Project Structure

```
Resume_Parser/
├── app.py                  # Flask routes & APIs
├── gemini_service.py       # Gemini AI service logic
├── resume_parser.py        # PDF/DOCX/TXT text extractor
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── uploads/                # Temporary uploads directory
├── static/
│   ├── css/
│   │   └── style.css       # Slate Gray & Warm Cream styling
│   └── js/
│       └── main.js         # Interactive client logic
└── templates/
    └── index.html          # Minimal single-page UI
```

---

## 📄 License
MIT License

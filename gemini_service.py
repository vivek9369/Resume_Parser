import os
import json
import re
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)

PRIMARY_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
    "gemini-pro"
]

def _get_api_key():
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)
    return os.getenv("GEMINI_API_KEY", "").strip()

def _strip_markdown_code_blocks(text):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def _call_gemini(prompt, system_instruction=None, temperature=0.2):
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in .env")
        
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    last_error = None
    for model_name in PRIMARY_MODELS:
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            }
            model_kwargs = {"model_name": model_name}
            if system_instruction:
                model_kwargs["system_instruction"] = system_instruction
                
            model = genai.GenerativeModel(**model_kwargs)
            response = model.generate_content(prompt, generation_config=generation_config)
            
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

def analyze_general_ats_score(resume_text):
    """
    Feature 1: Analyze raw resume and return ATS Score (0-100), section checks,
    extracted skills, strengths, and actionable improvements.
    """
    system_instruction = (
        "You are an expert ATS (Applicant Tracking System) Scanner & Executive Resume Auditor. "
        "Analyze the uploaded resume text for ATS readability, keyword strength, section hierarchy, "
        "and metric impact. Return STRICT, VALID JSON ONLY conforming to the exact schema."
    )
    
    prompt = f"""
Audit the following resume text for general ATS compliance and scoring.

SCHEMA REQUIRED:
{{
  "candidate_name": "Full Name or 'Candidate'",
  "candidate_role": "Primary Job Title / Discipline identified (e.g., Software Engineer, Marketing Specialist)",
  "ats_score": 82, // Integer 0 to 100
  "score_rating": "Strong ATS Profile", // "Excellent ATS Profile" (85-100), "Strong ATS Profile" (70-84), "Average Profile" (50-69), "Needs Improvement" (0-49)
  "summary": "2 sentence executive summary of the candidate's background and ATS readability.",
  "key_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5", "Skill 6"],
  "strengths": [
    "Identified strength 1 (e.g., Strong use of action verbs)",
    "Identified strength 2 (e.g., Clear chronological structure)",
    "Identified strength 3"
  ],
  "improvements": [
    "Actionable improvement 1 (e.g., Quantify achievements with percentage or revenue metrics)",
    "Actionable improvement 2 (e.g., Expand technical skills section with current industry tools)",
    "Actionable improvement 3"
  ],
  "formatting_checks": {{
    "contact_info": true,
    "clear_experience_dates": true,
    "measurable_metrics": true,
    "skills_section": true
  }}
}}

RESUME TEXT:
\"\"\"
{resume_text[:25000]}
\"\"\"
"""

    try:
        raw = _call_gemini(prompt, system_instruction=system_instruction, temperature=0.2)
        cleaned = _strip_markdown_code_blocks(raw)
        data = json.loads(cleaned)
        
        score = int(data.get("ats_score", 75))
        data["ats_score"] = max(0, min(100, score))
        return data
    except Exception as e:
        print(f"Fallback general ATS scoring: {e}")
        return _fallback_general_ats(resume_text)

def analyze_job_targeted_ats_score(resume_text, job_title, job_description):
    """
    Feature 2: Match resume against a specific Job Description and return
    targeted ATS score (0-100), matched keywords, missing keywords, and recommendations.
    """
    system_instruction = (
        "You are an AI Technical Recruiter and ATS Matching Engine. "
        "Score the candidate resume strictly against the provided Target Job Title and Job Description. "
        "Return STRICT, VALID JSON ONLY."
    )
    
    prompt = f"""
Evaluate the candidate's resume match against the target job.

TARGET JOB TITLE:
{job_title}

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

CANDIDATE RESUME:
\"\"\"
{resume_text[:25000]}
\"\"\"

SCHEMA REQUIRED:
{{
  "candidate_name": "Candidate Full Name or 'Candidate'",
  "target_job_title": "{job_title}",
  "ats_score": 88, // Integer 0 to 100 representing suitability for THIS specific role
  "match_level": "High Match", // "High Match" (80-100), "Moderate Match" (60-79), "Low Fit" (0-59)
  "match_summary": "2-3 sentences evaluating how well the candidate matches this specific job description.",
  "matching_skills": [
    "Skill/keyword present in both the resume and the job description"
  ],
  "missing_keywords": [
    "Important keyword or qualification mentioned in the job description that is missing/weak in the resume"
  ],
  "strengths_for_role": [
    "Why this candidate stands out for this particular role 1",
    "Why this candidate stands out 2"
  ],
  "ats_optimization_tips": [
    "Specific tweak to add to resume to beat ATS filter for this job 1",
    "Specific tweak to add to resume 2"
  ]
}}
"""

    try:
        raw = _call_gemini(prompt, system_instruction=system_instruction, temperature=0.2)
        cleaned = _strip_markdown_code_blocks(raw)
        data = json.loads(cleaned)
        
        score = int(data.get("ats_score", 70))
        data["ats_score"] = max(0, min(100, score))
        return data
    except Exception as e:
        print(f"Fallback job targeted scoring: {e}")
        return _fallback_job_match(resume_text, job_title, job_description)

# Graceful Heuristic Fallbacks
def _fallback_general_ats(resume_text):
    common_skills = [
        "Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS", "Git",
        "Communication", "Leadership", "Project Management", "Data Analysis", "HTML", "CSS"
    ]
    detected_skills = [s for s in common_skills if re.search(r'\b' + re.escape(s) + r'\b', resume_text, re.IGNORECASE)]
    if not detected_skills:
        detected_skills = ["Problem Solving", "Collaboration", "Technical Implementation"]
        
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_numbers = bool(re.search(r'\b\d+%\b|\$\d+|\b\d+\+\s*years\b', resume_text))
    
    score = 72
    if len(detected_skills) > 4:
        score += 10
    if has_numbers:
        score += 8
    score = max(50, min(95, score))

    return {
        "candidate_name": resume_text.split('\n')[0][:40].strip() or "Candidate",
        "candidate_role": "Technology Professional",
        "ats_score": score,
        "score_rating": "Strong ATS Profile" if score >= 75 else "Average Profile",
        "summary": "The resume has good foundational structure and relevant technical skills. Adding quantifiable metrics will elevate the score.",
        "key_skills": detected_skills,
        "strengths": [
            "Clear technical skill terminology",
            "Identifiable work experience flow",
            "Valid contact details structure"
        ],
        "improvements": [
            "Add quantifiable results (e.g., % improvement, revenue growth, users served)",
            "Include more action verbs at the start of each bullet point",
            "Ensure standard section headings (Experience, Education, Skills)"
        ],
        "formatting_checks": {
            "contact_info": has_email,
            "clear_experience_dates": True,
            "measurable_metrics": has_numbers,
            "skills_section": len(detected_skills) > 0
        }
    }

def _fallback_job_match(resume_text, job_title, job_description):
    jd_lower = job_description.lower()
    resume_lower = resume_text.lower()
    
    keywords = ["python", "javascript", "react", "sql", "docker", "aws", "kubernetes", "fastapi", "flask", "ci/cd", "agile", "leadership"]
    jd_keywords = [k for k in keywords if k in jd_lower]
    matched = [k.capitalize() for k in jd_keywords if k in resume_lower]
    missing = [k.capitalize() for k in jd_keywords if k not in resume_lower]
    
    score = 65
    if jd_keywords:
        match_ratio = len(matched) / len(jd_keywords)
        score = int(50 + (match_ratio * 45))
        
    return {
        "candidate_name": "Candidate",
        "target_job_title": job_title or "Target Position",
        "ats_score": max(45, min(95, score)),
        "match_level": "High Match" if score >= 78 else ("Moderate Match" if score >= 60 else "Low Fit"),
        "match_summary": f"Resume matches key requirements for {job_title}. Incorporating missing core keywords will improve ATS pass rate.",
        "matching_skills": matched if matched else ["Core Domain Skills", "Communication"],
        "missing_keywords": missing if missing else ["Industry-specific Frameworks", "Cloud Infrastructure"],
        "strengths_for_role": [
            f"Relevant experience matching {', '.join(matched[:3]) if matched else 'core requirements'}",
            "Strong functional background"
        ],
        "ats_optimization_tips": [
            f"Explicitly weave '{missing[0]}' into your latest job bullet point" if missing else "Include specific technologies from the job post",
            "Align your job title and summary with the exact wording of the job posting"
        ]
    }

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import resume_parser
import gemini_service

# Load environment
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'slate_gray_warm_cream_minimal_key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Minimal single-page UI for ATS Resume Screening."""
    return render_template('index.html')

@app.route('/api/score-resume', methods=['POST'])
def score_resume():
    """
    Feature 1: Upload resume and get instant general ATS score (pure in-memory).
    """
    if 'resume' not in request.files:
        return jsonify({"success": False, "error": "Please upload a resume file."}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected."}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file format. Please upload PDF, DOCX, or TXT."}), 400
        
    try:
        filename = secure_filename(file.filename)
        
        # Extract text directly in memory without writing to disk (serverless & cloud safe)
        resume_text = resume_parser.parse_resume_stream(file, filename=filename)
        
        # Analyze ATS score with Gemini
        ats_result = gemini_service.analyze_general_ats_score(resume_text)
        ats_result['filename'] = filename
        
        return jsonify({"success": True, "data": ats_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/match-job', methods=['POST'])
def match_job():
    """
    Feature 2: Enter job title/description + upload resume to get targeted ATS fit score (pure in-memory).
    """
    if 'resume' not in request.files:
        return jsonify({"success": False, "error": "Please upload a resume file."}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected."}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file format. Please upload PDF, DOCX, or TXT."}), 400
        
    job_title = request.form.get('job_title', '').strip() or "Target Position"
    job_description = request.form.get('job_description', '').strip()
    
    if not job_description:
        return jsonify({"success": False, "error": "Please enter a Job Description."}), 400
        
    try:
        filename = secure_filename(file.filename)
        
        # Extract text directly in memory without writing to disk (serverless & cloud safe)
        resume_text = resume_parser.parse_resume_stream(file, filename=filename)
        
        # Analyze targeted ATS match with Gemini
        match_result = gemini_service.analyze_job_targeted_ats_score(resume_text, job_title, job_description)
        match_result['filename'] = filename
        
        return jsonify({"success": True, "data": match_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n========================================================")
    print(f"[OK] Minimal ATS Resume Platform is running!")
    print(f"[OK] Local URL: http://127.0.0.1:{port}")
    print(f"[OK] Theme: Slate Gray (#708090) & Warm Cream (#FAF3E0)")
    print(f"========================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)

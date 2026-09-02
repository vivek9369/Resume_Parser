/**
 * Minimal ATS Resume Scanner - Client Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  setupDropzones();
  setupFormSubmissions();
});

function switchTab(mode) {
  const generalBtn = document.getElementById('tabGeneralBtn');
  const jobBtn = document.getElementById('tabJobBtn');
  const generalContent = document.getElementById('generalTabContent');
  const jobContent = document.getElementById('jobTabContent');
  const resultsCard = document.getElementById('resultsCard');

  if (mode === 'general') {
    generalBtn.classList.add('active');
    jobBtn.classList.remove('active');
    generalContent.classList.add('active');
    jobContent.classList.remove('active');
  } else {
    jobBtn.classList.add('active');
    generalBtn.classList.remove('active');
    jobContent.classList.add('active');
    generalContent.classList.remove('active');
  }
  
  if (resultsCard) {
    resultsCard.style.display = 'none';
  }
}

function setupDropzones() {
  setupSingleDropzone('generalDropzone', 'generalResumeInput', 'generalFilePill', 'generalFileName');
  setupSingleDropzone('jobDropzone', 'jobResumeInput', 'jobFilePill', 'jobFileName');
}

function setupSingleDropzone(dropzoneId, inputId, pillId, nameId) {
  const dropzone = document.getElementById(dropzoneId);
  const fileInput = document.getElementById(inputId);
  const filePill = document.getElementById(pillId);
  const fileName = document.getElementById(nameId);

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      showSelectedFile(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      showSelectedFile(fileInput.files[0]);
    }
  });

  function showSelectedFile(file) {
    if (filePill && fileName) {
      fileName.textContent = file.name + ` (${(file.size / 1024).toFixed(1)} KB)`;
      filePill.style.display = 'flex';
    }
  }
}

function setupFormSubmissions() {
  const generalForm = document.getElementById('generalScoreForm');
  const jobForm = document.getElementById('jobMatchForm');
  const loadingBox = document.getElementById('loadingBox');
  const resultsCard = document.getElementById('resultsCard');

  // Feature 1: General ATS Score Form
  if (generalForm) {
    generalForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fileInput = document.getElementById('generalResumeInput');
      if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select a resume file to upload.');
        return;
      }

      const formData = new FormData();
      formData.append('resume', fileInput.files[0]);

      resultsCard.style.display = 'none';
      loadingBox.style.display = 'block';
      loadingBox.scrollIntoView({ behavior: 'smooth' });

      try {
        const response = await fetch('/api/score-resume', {
          method: 'POST',
          body: formData
        });
        const res = await response.json();
        loadingBox.style.display = 'none';

        if (res.success && res.data) {
          renderGeneralATSResults(res.data);
        } else {
          alert('Error: ' + (res.error || 'Failed to score resume.'));
        }
      } catch (err) {
        loadingBox.style.display = 'none';
        alert('Network Error: ' + err.message);
      }
    });
  }

  // Feature 2: Job-Targeted Match Form
  if (jobForm) {
    jobForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fileInput = document.getElementById('jobResumeInput');
      const title = document.getElementById('jobTitle').value.trim();
      const desc = document.getElementById('jobDescription').value.trim();

      if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please upload a resume file.');
        return;
      }
      if (!desc) {
        alert('Please enter the Job Description.');
        return;
      }

      const formData = new FormData();
      formData.append('resume', fileInput.files[0]);
      formData.append('job_title', title);
      formData.append('job_description', desc);

      resultsCard.style.display = 'none';
      loadingBox.style.display = 'block';
      loadingBox.scrollIntoView({ behavior: 'smooth' });

      try {
        const response = await fetch('/api/match-job', {
          method: 'POST',
          body: formData
        });
        const res = await response.json();
        loadingBox.style.display = 'none';

        if (res.success && res.data) {
          renderJobTargetedResults(res.data);
        } else {
          alert('Error: ' + (res.error || 'Failed to match against job description.'));
        }
      } catch (err) {
        loadingBox.style.display = 'none';
        alert('Network Error: ' + err.message);
      }
    });
  }

  function renderGeneralATSResults(data) {
    resultsCard.innerHTML = `
      <!-- Hero Score Box -->
      <div class="score-hero-box">
        <div class="score-number-group">
          <div class="score-circle">
            <span class="score-val">${data.ats_score}</span>
            <span class="score-max">out of 100</span>
          </div>
          <div>
            <div class="score-text-title">${escapeHtml(data.score_rating || 'ATS Score')}</div>
            <div class="score-text-desc">${escapeHtml(data.candidate_name || 'Candidate')} &bull; ${escapeHtml(data.candidate_role || 'Profile')}</div>
          </div>
        </div>
        <button class="tab-btn" onclick="window.print()" style="background: var(--slate-dark); color: var(--warm-cream); padding: 0.6rem 1.2rem;">
          Print / Save PDF
        </button>
      </div>

      <!-- Candidate Snapshot -->
      <div style="margin-bottom: 1.5rem;">
        <p style="font-size: 0.98rem; color: var(--text-main); line-height: 1.6;">${escapeHtml(data.summary || '')}</p>
      </div>

      <!-- Extracted Skills -->
      <div class="breakdown-section">
        <div class="breakdown-title">
          <svg style="width: 18px; height: 18px; color: var(--slate-gray);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          Detected ATS Keywords & Skills:
        </div>
        <div>
          ${(data.key_skills || []).map(s => `<span class="pill-tag">${escapeHtml(s)}</span>`).join('')}
        </div>
      </div>

      <!-- Key Strengths -->
      ${data.strengths && data.strengths.length > 0 ? `
        <div class="breakdown-section">
          <div class="breakdown-title" style="color: var(--accent-success);">
            <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            What Your Resume Does Well:
          </div>
          <ul class="bullet-list">
            ${data.strengths.map(st => `<li>${escapeHtml(st)}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      <!-- Actionable Improvements -->
      ${data.improvements && data.improvements.length > 0 ? `
        <div class="breakdown-section">
          <div class="breakdown-title" style="color: var(--slate-deep);">
            <svg style="width: 18px; height: 18px; color: var(--accent-warning);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            Actionable Recommendations to Boost Score:
          </div>
          <ul class="bullet-list">
            ${data.improvements.map(imp => `<li>${escapeHtml(imp)}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
    `;

    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({ behavior: 'smooth' });
  }

  function renderJobTargetedResults(data) {
    resultsCard.innerHTML = `
      <!-- Hero Score Box -->
      <div class="score-hero-box">
        <div class="score-number-group">
          <div class="score-circle">
            <span class="score-val">${data.ats_score}</span>
            <span class="score-max">match score</span>
          </div>
          <div>
            <div class="score-text-title">${escapeHtml(data.match_level || 'Job Fit')}</div>
            <div class="score-text-desc">Target Role: <strong>${escapeHtml(data.target_job_title || 'Position')}</strong></div>
          </div>
        </div>
        <button class="tab-btn" onclick="window.print()" style="background: var(--slate-dark); color: var(--warm-cream); padding: 0.6rem 1.2rem;">
          Print / Save PDF
        </button>
      </div>

      <!-- Match Summary -->
      <div style="margin-bottom: 1.5rem;">
        <p style="font-size: 0.98rem; color: var(--text-main); line-height: 1.6;">${escapeHtml(data.match_summary || '')}</p>
      </div>

      <!-- Matched vs Missing Keywords -->
      <div class="breakdown-section" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem;">
        <div>
          <div class="breakdown-title" style="color: var(--accent-success);">
            &check; Matched Keywords:
          </div>
          <div>
            ${(data.matching_skills || []).map(s => `<span class="pill-tag pill-matched">${escapeHtml(s)}</span>`).join('')}
          </div>
        </div>

        <div>
          <div class="breakdown-title" style="color: var(--accent-danger);">
            &times; Missing Critical Keywords:
          </div>
          <div>
            ${(data.missing_keywords || []).map(k => `<span class="pill-tag pill-missing">${escapeHtml(k)}</span>`).join('')}
          </div>
        </div>
      </div>

      <!-- Strengths for Role -->
      ${data.strengths_for_role && data.strengths_for_role.length > 0 ? `
        <div class="breakdown-section">
          <div class="breakdown-title" style="color: var(--slate-deep);">
            Why You Stand Out:
          </div>
          <ul class="bullet-list">
            ${data.strengths_for_role.map(st => `<li>${escapeHtml(st)}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      <!-- ATS Optimization Tips -->
      ${data.ats_optimization_tips && data.ats_optimization_tips.length > 0 ? `
        <div class="breakdown-section">
          <div class="breakdown-title" style="color: var(--slate-dark);">
            How to Tailor Your Resume for This Specific Job:
          </div>
          <ul class="bullet-list">
            ${data.ats_optimization_tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
    `;

    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({ behavior: 'smooth' });
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

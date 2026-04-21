# AI Resume Analyzer

An AI-powered resume analysis tool that evaluates resumes using NLP, semantic matching, and role-based scoring.

---

## Features

* Resume parsing (PDF/DOCX)
* Semantic skill extraction
* Auto role detection with confidence scoring
* Dynamic scoring system:

  * Base (skills)
  * Education
  * Experience
  * Impact
  * Penalty
* Skill gap analysis with suggestions
* Basic ATS compatibility checks

---

## Tech Stack

* Python
* Streamlit
* spaCy
* pdfplumber
* python-docx

---

## How to Run

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
cd ai-resume-analyzer

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

streamlit run app.py
```

---

## Scoring Logic

Score = Base + Education + Experience + Impact - Penalty

---

## Limitations

* Relies on keyword + semantic matching (limited context understanding)
* Static skills database
* Heuristic-based role detection

---

## Future Improvements

* Resume vs Job Description matching
* LLM-based personalized feedback
* Skill visualization dashboard

---

## Project Highlights

* Designed modular NLP pipeline
* Implemented hybrid AI scoring system
* Built interpretable and explainable evaluation model

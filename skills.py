import json
import os

JSON_PATH = os.path.join(os.path.dirname(__file__), "skills.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    _data = json.load(f)

SKILLS = _data["SKILLS"]
ROLE_KEYWORDS = _data["ROLE_KEYWORDS"]
ROLE_CATEGORIES = _data["ROLE_CATEGORIES"]
SYNONYMS = _data["SYNONYMS"]
CATEGORY_WEIGHTS = _data.get("CATEGORY_WEIGHTS", {})

def get_all_skills():
    """Returns a flat list of all skills across categories."""
    all_skills = []
    for category, skills in SKILLS.items():
        all_skills.extend(skills)
    return all_skills

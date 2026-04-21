import re
from skills import SKILLS, ROLE_CATEGORIES, CATEGORY_WEIGHTS

def _get_skill_names(found_category_list):
    """Helper to extract raw string names from objects."""
    if not found_category_list:
        return []
    if isinstance(found_category_list[0], dict):
        return [item['skill'] for item in found_category_list]
    return found_category_list

def calculate_base_score(found_skills, role):
    categories = ROLE_CATEGORIES.get(role, ["programming", "tools"])

    total_score = 0
    total_weight = 0

    for category in categories:
        skills = SKILLS.get(category, [])
        found_in_category = found_skills.get(category, [])
        
        if len(skills) == 0:
            continue
            
        weight = CATEGORY_WEIGHTS.get(category, 1)
        
        if found_in_category and isinstance(found_in_category[0], dict):
            category_points = sum([item['weight'] for item in found_in_category])
        else:
            category_points = len(found_in_category)
            
        category_ratio = min(category_points / max(1, len(skills) * 0.5), 1.0)
        
        total_score += category_ratio * weight
        total_weight += weight
        
    if total_weight == 0:
        return 0

    # User fix: Normalized Semantic Score (lower base impact)
    return round((total_score / total_weight) * 100 * 0.7, 2)

def penalty(found_skills, role):
    categories = ROLE_CATEGORIES.get(role, ["programming", "tools"])
    penalty_score = 0

    for category in categories:
        total = len(SKILLS.get(category, []))
        found_names = _get_skill_names(found_skills.get(category, []))
        found = len(found_names)
        
        if total == 0:
            continue
        missing_ratio = (total - found) / total

        # penalize only if heavily lacking
        if missing_ratio > 0.7:
            penalty_score += 5

    return penalty_score

def education_score(text):
    text = text.lower()
    score = 0

    if "b.s" in text or "bachelor" in text or "bsc" in text:
        score += 8
    if "computer science" in text:
        score += 5
    if "gpa" in text:
        score += 2
    if "master" in text or "m.s" in text or "msc" in text:
        score += 10

    return score

def experience_score(text):
    text = text.lower()
    score = 0

    if "intern" in text:
        score += 5
    if "experience" in text:
        score += 5
    if "developed" in text or "built" in text:
        score += 5
    if "project" in text:
        score += 5
    if "teaching assistant" in text or "ta " in text:
        score += 3

    return score

def experience_duration_bonus(text):
    years = re.findall(r'\b(20\d{2})\b', text)
    if len(years) >= 2:
        return 5
    return 0

def detect_impact(text):
    score = 0
    if re.search(r'\d+%', text):
        score += 5
    if re.search(r'\d+\s*(users|projects|clients|dollars|\$)', text):
        score += 5
    return score

def document_diagnostics(text):
    warnings = []
    word_count = len(text.split())
    
    if word_count < 300:
        warnings.append(f"Length: Too short ({word_count} words). Aim for 400+ words to pass ATS parsing heuristics.")
        
    num_metrics = len(re.findall(r'\d+', text))
    if num_metrics < 3:
        warnings.append("Impact: Very few numbers/metrics found. Provide quantified achievements.")
        
    return warnings

def final_score(base_score, text, found_skills, role):
    edu = education_score(text)
    
    # Cap experience and impact as per user fix
    exp = min(experience_score(text), 15)
    impact = min(detect_impact(text), 10)
    duration = experience_duration_bonus(text)
    
    pen = penalty(found_skills, role)

    score = base_score + edu + exp + duration + impact - pen

    # Score Dampening for realistic caps
    if score > 75:
        score = 75 + (score - 75) * 0.5

    final_val = max(0, min(100, round(score, 2)))
    
    rating = "Beginner"
    if final_val >= 80:
        rating = "Expert"
    elif final_val >= 50:
        rating = "Intermediate"
        
    metrics = {
        "base_score": base_score,
        "education": edu,
        "experience": exp + duration,
        "impact": impact,
        "penalty": pen
    }
        
    return final_val, rating, metrics

def identify_missing_skills(found_skills, target_role="General"):
    missing_skills = {}
    categories = ROLE_CATEGORIES.get(target_role, ["programming", "tools"])
    
    for category in categories:
        category_skills = SKILLS.get(category, [])
        if not category_skills:
            continue
        found_names = _get_skill_names(found_skills.get(category, []))
        missing = [skill for skill in category_skills if skill not in found_names]
        if missing:
            missing_skills[category] = missing
            
    return missing_skills

def generate_suggestions(missing_skills, found_skills, target_role="General"):
    suggestions = []
    for category, missing in missing_skills.items():
        if len(missing) > 0:
            top_missing = ", ".join(missing[:3])
            suggestions.append(f"To strengthen your application for {target_role}, consider highlighting '{category.replace('_', ' ').title()}' skills like: {top_missing}.")
            
    if not suggestions:
        suggestions.append(f"Your resume matches the target profile for {target_role} perfectly!")
        
    return suggestions

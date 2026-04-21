import re
from skills import SKILLS, ROLE_KEYWORDS, SYNONYMS

# Initialize Sentence Transformers lazily so app starts fast unless processing
embedding_model = None

# Initialize Scikit-Learn tools lazily
vectorizer = None
role_classifier = None

STRONG_WORDS = ["developed", "built", "implemented", "designed", "led", "architected", "optimized"]
WEAK_WORDS = ["basic", "familiar", "knowledge", "learning", "exposure to", "beginner"]

def _init_models():
    """Load semantic and role models asynchronously upon first use."""
    global embedding_model, vectorizer, role_classifier
    if embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            pass

    if role_classifier is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            
            # Synthesize training data from ROLE_KEYWORDS
            X_train = []
            y_train = []
            for role, keywords in ROLE_KEYWORDS.items():
                X_train.append(" ".join(keywords))
                y_train.append(role)
                
            vectorizer = TfidfVectorizer()
            X_vec = vectorizer.fit_transform(X_train)
            
            role_classifier = LogisticRegression(random_state=42)
            role_classifier.fit(X_vec, y_train)
        except ImportError:
            pass

def clean_text(text):
    return text.lower()

def get_context_strength(text, skill):
    """
    Looks for strong/weak words in a 60 character window around the skill to determine strength.
    """
    skill_idx = text.find(skill)
    if skill_idx == -1:
        return 1.0
        
    start = max(0, skill_idx - 60)
    end = min(len(text), skill_idx + len(skill) + 60)
    window = text[start:end]
    
    if any(w in window for w in STRONG_WORDS):
        return 2.0
    elif any(w in window for w in WEAK_WORDS):
        return 0.5
    return 1.0

def semantic_match(skill, text_sentences):
    """Fallback semantic matcher."""
    if embedding_model is None:
        return False
    from sentence_transformers import util
    skill_emb = embedding_model.encode(skill)
    
    # Check each sentence or chunk for semantic hit
    for sentence in text_sentences:
        sent_emb = embedding_model.encode(sentence)
        score = util.cos_sim(skill_emb, sent_emb).item()
        if score > 0.75:
            return True
    return False

def extract_skills(text):
    """
    Extracts skills using syntax constraints, synonyms, semantic fallback, and returns weights.
    Returns: { category: [{'skill': 'python', 'weight': 1.0}, ...] }
    """
    _init_models()
    
    found_skills = {category: [] for category in SKILLS}
    cleaned = clean_text(text)
    
    # Basic chunks for semantic parsing
    sentences = [s.strip() for s in re.split(r'[.?!]', cleaned) if len(s.strip()) > 10]

    for category, skills_list in SKILLS.items():
        for skill in skills_list:
            
            # 1. Expand synonyms mapped to this skill
            variants = [skill] + SYNONYMS.get(skill, [])
            
            matched = False
            for variant in variants:
                escaped_variant = re.escape(variant)
                pattern = r'(?<![a-z0-9])' + escaped_variant + r'(?![a-z0-9])'
                
                if re.search(pattern, cleaned):
                    matched = True
                    break
                    
            # 2. If no exact match, try semantic fallback (costly)
            if not matched and len(skill) > 3: # Ignore short skills for semantic
                 matched = semantic_match(skill, sentences)
            
            if matched:
                weight = get_context_strength(cleaned, skill)
                found_skills[category].append({'skill': skill, 'weight': weight})
                
    return found_skills

def detect_role(text):
    text = text.lower()
    scores = {}

    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[role] = score

    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if not sorted_roles:
        return "Undetermined", scores

    best_role, best_score = sorted_roles[0]
    
    if len(sorted_roles) > 1:
        second_score = sorted_roles[1][1]
    else:
        second_score = 0

    if best_score == 0:
        return "Undetermined", scores

    if best_score - second_score < 2:
        return "General", scores  

    return best_role, scores

def detect_multiple_roles(text):
    text = text.lower()
    roles = []

    for role, keywords in ROLE_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        if count >= 4:  
            roles.append(role)

    return roles

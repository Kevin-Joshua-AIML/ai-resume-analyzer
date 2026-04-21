import os
import unittest
from nlp_processing import extract_skills, detect_role, detect_multiple_roles
from scoring import calculate_base_score, final_score, identify_missing_skills

class TestResumeAnalyzer(unittest.TestCase):
    def test_role_detection(self):
        text = "I am a Data Scientist. I use python, pandas, numpy, machine learning, and pytorch."
        # Because we test exact substrings, we expect role keywords to be hit
        role, scores = detect_role(text)
        self.assertEqual(role, "Data Scientist")
        
        roles = detect_multiple_roles(text)
        self.assertIn("Data Scientist", roles)

    def test_bonus_scoring(self):
        text = """
        B.S. in Computer Science. Graduated in 2020. Worked there until 2025.
        I am a software engineer intern. I built and developed a project testing python code.
        """
        found_skills = extract_skills(text)
        base = calculate_base_score(found_skills, "Software Engineer")
        
        score, rating, metrics = final_score(base, text, found_skills, "Software Engineer")
        
        self.assertTrue(metrics['education'] > 0)
        self.assertTrue(metrics['experience'] > 0)
        
    def test_empty_text(self):
        # Simulating empty text extraction
        text = "   "
        found_skills = extract_skills(text)
        self.assertEqual(sum(len(v) for v in found_skills.values()), 0)
        
        base = calculate_base_score(found_skills, "General")
        score, rating, metrics = final_score(base, text, found_skills, "General")
        self.assertEqual(score, 0)
        
        missing = identify_missing_skills(found_skills, "General")
        self.assertTrue(len(missing.get('programming', [])) > 0)

    def test_non_resume_file(self):
        text = "Hello world, this is just a random document talking about apples and oranges."
        found_skills = extract_skills(text)
        self.assertEqual(sum(len(v) for v in found_skills.values()), 0)
        base = calculate_base_score(found_skills, "General")
        score, rating, metrics = final_score(base, text, found_skills, "General")
        self.assertEqual(score, 0)
        
if __name__ == "__main__":
    unittest.main()

import streamlit as st
from text_extraction import extract_text
from nlp_processing import extract_skills, detect_role, detect_multiple_roles
from scoring import calculate_base_score, final_score, identify_missing_skills, generate_suggestions, document_diagnostics
from skills import ROLE_CATEGORIES

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume (PDF or DOCX) to get a semantic, skill-based score and advanced ATS diagnostics.")

role_options = list(ROLE_CATEGORIES.keys())
target_role = st.selectbox("Target Role (Adjust to change metric scopes)", role_options, index=role_options.index("General"))

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    st.info(f"File uploaded successfully: {uploaded_file.name}")
    
    with st.spinner("Decoding semantics and analyzing context..."):
        try:
            # Extract Text
            text = extract_text(uploaded_file, uploaded_file.name)
            
            if not text or len(text.strip()) == 0:
                st.error("Error: The extracted text is empty. Please ensure your PDF or DOCX file contains valid text and is not just scanned images.")
            else:
                # Extract Data
                found_skills = extract_skills(text)
                auto_role, role_scores = detect_role(text)
                hybrid_roles = detect_multiple_roles(text)
                
                # ATS Diag
                ats_warnings = document_diagnostics(text)
                
                # Scoring
                base_score = calculate_base_score(found_skills, target_role)
                score, rating, metrics = final_score(base_score, text, found_skills, target_role)
                
                missing_skills = identify_missing_skills(found_skills, target_role)
                suggestions = generate_suggestions(missing_skills, found_skills, target_role)
                
                # DISPLAY RESULTS
                st.divider()
                st.subheader("📊 Analysis Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label=f"Final Pipeline Score ({target_role})", value=f"{score}/100")
                with col2:
                    st.metric(label="Skill Rating", value=rating)
                with col3:
                    st.metric(label="Auto-Detected Best Role", value=auto_role)

                st.markdown("### 🔍 Role Confidence")
                sorted_conf = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                if sorted_conf:
                    for role_name, conf_score in sorted_conf:
                        if conf_score > 0:
                            st.write(f"- **{role_name}**: {conf_score}")
                else:
                    st.write("No strong roles detected.")

                if len(hybrid_roles) > 1:
                    st.info(f"Hybrid Resume Detected! Alignment found in: {', '.join(hybrid_roles)}")
                    
                # Show advanced metrics
                st.markdown("### 🔢 Scoring Breakdown")
                st.caption("Score = Base + Edu + Exp + Impact - Penalty")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Semantic Base", f"{metrics['base_score']}")
                m2.metric("Education", f"+{metrics['education']}")
                m3.metric("Experience", f"+{metrics['experience']}")
                m4.metric("Impact", f"+{metrics['impact']}")
                m5.metric("Penalty", f"-{metrics['penalty']}")
                    
                # ATS Warnings
                if ats_warnings:
                    st.error("⚠️ ATS Weaknesses Detected")
                    for w in ats_warnings:
                        st.write(f"- {w}")
                else:
                    st.success("✅ Passed basic ATS structural gates!")
                    
                st.markdown("### ✅ Identified Capabilities (with strengths)")
                has_skills = False
                for category, skills in found_skills.items():
                    if skills:
                        has_skills = True
                        # skills is a list of dicts: {'skill': x, 'weight': y}
                        formatted_skills = [f"{item['skill']} (x{item['weight']})" for item in skills]
                        st.markdown(f"**{category.replace('_', ' ').title()}:** {', '.join(formatted_skills)}")
                
                if not has_skills:
                    st.warning("No matching skills found in the resume. Please ensure you have clearly listed technical and soft skills that match industry standards.")
                
                st.markdown(f"### ❌ Missing Core Skills for {target_role}")
                if sum(len(m) for m in missing_skills.values()) == 0:
                    st.success("No missing skills for this target profile!")
                else:
                    for category, skills in missing_skills.items():
                        if skills:
                            with st.expander(f"Missing from {category.replace('_', ' ').title()}"):
                                st.write(", ".join(skills))
                
                st.markdown("### 💡 Suggestions for Improvement")
                for suggestion in suggestions:
                    st.info(suggestion)
                    
        except ValueError as ve:
            st.error(f"Error handling file: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

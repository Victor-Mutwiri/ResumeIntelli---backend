from sentence_transformers import SentenceTransformer
from groq import Groq
from typing import List
import re

class ResumeAnalyzer:
    """
    A class to analyze the match between a resume and job description.
    """
    def __init__(self, groq_api_key):
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.max_token_limit = 15000
        self.used_tokens = 0

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using simple keyword matching."""
        skill_indicators = ['proficient in', 'experience with', 'skilled in', 
                            'knowledge of', 'familiar with', 'expertise in']
        skills = set()
        sentences = text.lower().split('.')
        
        for sentence in sentences:
            for indicator in skill_indicators:
                if indicator in sentence:
                    parts = sentence.split(indicator)
                    if len(parts) > 1:
                        potential_skills = re.split(r'[,;&]', parts[1])
                        skills.update(skill.strip() for skill in potential_skills if skill.strip())
        
        return list(skills)
    
    def generate_custom_resume_logic(self, resume_text: str, job_description: str) -> str:
        """
        Generate a custom resume by incorporating job description details.
        """
        # Example prompt for a language model
        prompt = (
            f"User Resume: {resume_text}\n\n"
            f"Job Description: {job_description}\n\n"
            "Create a custom resume that highlights the user's skills and experience "
            "while incorporating relevant details from the job description."
        )
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )
            custom_resume = response.choices[0].message.content
        except Exception as e:
            custom_resume = f"An error occurred while generating the custom resume: {e}"
        
        return custom_resume


    def analyze_match_with_groq(self, resume_text: str, job_description: str) -> str:
        """
        Analyze how well a resume matches a job description using Groq.
        """
        if self.used_tokens >= self.max_token_limit:
            return "Token limit reached. Please try again later."
        
        prompt = [
            {"role": "system", "content": "You are a career coach assessing a resume against a job description."},
            {"role": "user", "content": f"Job Description: {job_description}"},
            {"role": "user", "content": f"Resume: {resume_text}"},
            {"role": "user", "content": (
                "Please provide a detailed analysis of how well this resume matches the job description. "
                "Include the following sections:\n"
                "1. Key Skills Match: List the skills that align well with the job requirements\n"
                "2. Missing Skills: Identify important skills from the job description that are not evident in the resume\n"
                "3. Experience Alignment: Evaluate how well the candidate's experience matches the role\n"
                "4. Improvement Suggestions: Specific recommendations for strengthening the application\n"
                "5. Overall Rating: Score from 1-10 (10 being perfect match) with brief explanation\n\n"
                "Focus on concrete evidence from the resume without making assumptions about unlisted skills."
            )}
        ]
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=prompt,
                model="llama3-8b-8192"
            )
            feedback = response.choices[0].message.content
            # Estimate tokens used
            self.used_tokens += len(resume_text.split()) + len(job_description.split())
        except Exception as e:
            feedback = f"An error occurred while analyzing with Groq: {e}"
        
        return feedback

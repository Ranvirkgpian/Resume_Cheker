import json
from openai import OpenAI
from src.llm.base import BaseLLMClient
from src.core.models import CandidateProfile, JobDescription, EvaluationResult

class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"

    def evaluate_candidate(self, candidate: CandidateProfile, jd: JobDescription) -> EvaluationResult:
        prompt = f"""
You are an expert technical recruiter and engineering manager. Evaluate the following candidate resume against the provided Job Description.

Analyze the profile across these 4 dimensions:
1. Exact Match: Direct keyword or requirement matches.
2. Similarity Match: Semantic equivalency (e.g., matching AWS Kinesis to Kafka experience). Be smart about transferable skills.
3. Impact/Achievement: Assessing the depth and scale of achievements (e.g., metrics, business impact).
4. Ownership: Evaluating the candidate's level of responsibility and autonomy.

For EACH dimension, provide:
- A score (0-100)
- A concise explanation
- A list of actionable improvement suggestions (how the candidate can improve their resume for this dimension)
- A list of matched keywords/skills found in the resume
- A list of missing keywords/skills NOT found in the resume but required by the JD

Then provide an overall score (0-100) and classify them into a Tier:
- "A" (Strong Shortlist — Fast-track to interview)
- "B" (Needs Improvement — Likely shortlist with gaps)
- "C" (Low Match — Significant gaps)

Also provide:
- section_scores: Score each resume SECTION individually (Education, Experience, Projects, Skills). For each provide a score (0-100) and a brief explanation.
- requirement_matches: For each key requirement from the JD, indicate whether it was matched in the resume, provide a match_percent (0-100), and cite evidence from the resume.

Finally, provide a brief summary of their fit.

Output purely as a JSON object matching this schema exactly:
{{
  "scores": {{
    "exact_match": {{"score": int, "explanation": "string", "suggestions": ["string"], "matched_keywords": ["string"], "missing_keywords": ["string"]}},
    "similarity_match": {{"score": int, "explanation": "string", "suggestions": ["string"], "matched_keywords": ["string"], "missing_keywords": ["string"]}},
    "impact_achievement": {{"score": int, "explanation": "string", "suggestions": ["string"], "matched_keywords": ["string"], "missing_keywords": ["string"]}},
    "ownership": {{"score": int, "explanation": "string", "suggestions": ["string"], "matched_keywords": ["string"], "missing_keywords": ["string"]}},
    "overall_score": int
  }},
  "tier": "A" | "B" | "C",
  "summary": "string",
  "section_scores": [
    {{"section": "Education", "score": int, "explanation": "string"}},
    {{"section": "Experience", "score": int, "explanation": "string"}},
    {{"section": "Projects", "score": int, "explanation": "string"}},
    {{"section": "Skills", "score": int, "explanation": "string"}}
  ],
  "requirement_matches": [
    {{"requirement": "string", "matched": true/false, "match_percent": int, "evidence": "string"}}
  ]
}}

--- JOB DESCRIPTION ---
{jd.raw_text}

--- RESUME ---
{candidate.raw_text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise JSON-outputting evaluation system. Do not include markdown formatting like ```json in the output, just the raw JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_json = response.choices[0].message.content
        return EvaluationResult.model_validate_json(result_json)

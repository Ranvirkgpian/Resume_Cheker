import json
from openai import OpenAI
from src.llm.base import BaseLLMClient
from src.core.models import CandidateProfile, JobDescription, EvaluationResult

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-2024-08-06"

    def evaluate_candidate(self, candidate: CandidateProfile, jd: JobDescription) -> EvaluationResult:
                prompt = f"""
You are an expert, domain-agnostic recruiter. Evaluate the candidate resume STRICTLY against the provided Job Description (JD). Do NOT use any external or default skill lists.

CRITICAL RULES:
1. Dynamic Parsing: Extract Required Skills, Preferred Skills, Responsibilities, and Tools directly from the JD.
2. Strict Context: Compare the resume ONLY against the extracted JD skills.
   - Matched Skills: MUST be present in both JD and Resume.
   - Missing Skills: MUST be present in JD but absent in Resume.
   - NEVER introduce skills or tools not explicitly mentioned in the JD or logically derived from the JD domain. No cross-domain hallucinations (e.g., do not suggest Kafka for a Civil Engineering role).
3. Role-Sensitivity:
   - If the JD is for an Internship/Fresher: focus Impact on "Project Outcomes" and "Learning Impact", and Ownership on "initiative/contribution".
   - If Experienced: focus Impact on "Business Impact" (ROI, revenue, efficiency), and Ownership on "leadership/autonomy".
4. Intelligent Suggestions: Generate actionable suggestions purely based on JD gaps. E.g., if a JD tool is missing, suggest adding a project using that tool. Do not give generic suggestions.

Analyze across 4 dimensions:
1. Exact Match: Direct keyword/requirement matches from the JD.
2. Similarity Match: Semantic equivalency within the SAME domain (e.g., AWS Kinesis to Kafka if tech, or STAAD to SAP2000 if civil).
3. Impact/Achievement: Scale of achievements adapted to role level.
4. Ownership: Level of responsibility adapted to role level.

For EACH dimension, provide:
- A score (0-100)
- A concise explanation
- A list of actionable improvement suggestions
- A list of matched keywords/skills (JD vs Resume)
- A list of missing keywords/skills (JD vs Resume)

Provide an overall score (0-100) and classify them into a Tier:
- "A" (Strong match: 85-100)
- "B" (Moderate match: 70-84)
- "C" (Weak match: <70)

Also provide:
- section_scores: Score each resume SECTION individually (Education, Experience, Projects, Skills) based on relevance to JD. Provide a score (0-100) and brief explanation.
- requirement_matches: For each key requirement extracted from the JD, indicate whether it was matched, provide a match_percent (0-100), and cite evidence from the resume.

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

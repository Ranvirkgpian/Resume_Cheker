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
You are an expert, domain-agnostic recruiter. Evaluate the candidate resume STRICTLY against the provided Job Description (JD). Do NOT use any external or default skill lists.

CRITICAL RULES:
1. Skill Normalization (CRITICAL BUG FIX): Before matching, normalize all skills by converting to lowercase, removing punctuation, and standardizing formats (e.g., "STAAD.Pro" = "STAAD Pro", "MS Excel" = "Excel", "Auto-CAD" = "AutoCAD"). Treat normalized skills as identical.
2. Dynamic Parsing & Evidence-Based Validation: Extract Required Skills, Preferred Skills, Responsibilities, and Tools directly from the JD. Search the ENTIRE resume (skills, projects, experience) before marking anything as missing. Do not rely only on the "Skills" section.
3. Semantic Skill Matching & Synonym Mapping Layer: Evaluate conceptual similarity and synonyms.
   - If similarity > 0.75 (e.g., "AutoCAD" ≈ "Revit", "Geotechnical Engineering concepts" ≈ "Geotechnical Engineering", "Programming" ≈ "Python"), mark it as MATCHED.
4. Smart Missing Skills Detection: Only mark a skill as missing if it exists in the JD AND no direct OR semantic/normalized match is found anywhere in the resume. Remove false missing skills.
5. Exact vs Semantic Confidence Fix: For every item in the `matched_keywords` list, append a confidence rating based on the match type:
   - Append "(High)" for direct exact mentions (e.g., AutoCAD <-> AutoCAD).
   - Append "(Medium)" for semantic/synonym equivalents (e.g., AutoCAD <-> Revit).
6. Suggestion Precision Upgrade & Redundancy Removal:
   - NEVER suggest "learning" or "adding" a skill if it is already present directly or semantically.
   - If a skill exists, suggest "showing usage" (e.g., "Show how Python was used in projects or analysis").
   - If a skill is truly missing, suggest a specific contextual addition (e.g., "If AutoCAD not used, highlight equivalent BIM tools like Revit").
7. Internship-Safe Ownership Logic:
   - For internships/student resumes, DO NOT expect or evaluate leadership/team management. Evaluate initiative and independent work instead. Replace "Missing: Leadership" with "Opportunity: Can further highlight initiative or leadership signals in projects".
   - For Experienced roles, focus on Business Impact, ROI, and Leadership.
8. Final Validation Rule: Before outputting, ensure there are no false missing skills, no duplicate/redundant suggestions, and confidence levels are consistent.

Analyze across 4 dimensions:
1. Exact Match: Direct keyword/requirement matches from the JD.
2. Similarity Match: Semantic equivalency and synonym mapping within the SAME domain.
3. Impact/Achievement: Scale of achievements adapted to role level.
4. Ownership: Level of responsibility adapted to role level.

For EACH dimension, provide:
- A score (0-100)
- A concise explanation
- A list of highly specific, context-aware improvement suggestions (NO redundant suggestions)
- A list of matched keywords/skills (MUST include confidence score, e.g., "Python (High)", "BIM tools (Medium)")
- A list of truly missing keywords/skills

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

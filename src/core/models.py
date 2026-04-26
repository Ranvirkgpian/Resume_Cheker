from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TierClassification(str, Enum):
    TIER_A = "A" # Fast-track
    TIER_B = "B" # Technical Screen
    TIER_C = "C" # Needs Evaluation

TIER_DESCRIPTIONS = {
    "A": "Strong Shortlist — Fast-track to interview. Candidate closely matches all key requirements.",
    "B": "Needs Improvement — Likely shortlist, but has gaps to address before proceeding.",
    "C": "Low Match — Significant skill or experience gaps. Requires further evaluation.",
}

class ScoreDimension(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Score from 0 to 100")
    explanation: str = Field(..., description="Explanation of why this score was given")
    suggestions: List[str] = Field(default_factory=list, description="Actionable improvement suggestions")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords/skills that matched")
    missing_keywords: List[str] = Field(default_factory=list, description="Keywords/skills that are missing")

class EvaluationScores(BaseModel):
    exact_match: ScoreDimension = Field(..., description="Direct keyword or requirement matches")
    similarity_match: ScoreDimension = Field(..., description="Semantic equivalency (e.g. AWS Kinesis = Kafka)")
    impact_achievement: ScoreDimension = Field(..., description="Depth and scale of achievements (metrics, business impact)")
    ownership: ScoreDimension = Field(..., description="Candidate's level of responsibility and autonomy")
    overall_score: int = Field(..., ge=0, le=100, description="Weighted average or holistic overall score")

class SectionScore(BaseModel):
    section: str = Field(..., description="Resume section name, e.g. Education, Experience, Projects, Skills")
    score: int = Field(..., ge=0, le=100, description="Score for this section from 0 to 100")
    explanation: str = Field(..., description="Brief explanation for this section's score")

class RequirementMatch(BaseModel):
    requirement: str = Field(..., description="A specific requirement from the Job Description")
    matched: bool = Field(..., description="Whether this requirement was matched in the resume")
    match_percent: int = Field(..., ge=0, le=100, description="Percentage match for this requirement")
    evidence: str = Field(..., description="Evidence from the resume that matches or shows gap")

class EvaluationResult(BaseModel):
    scores: EvaluationScores
    tier: TierClassification = Field(..., description="Classification tier based on scores")
    summary: str = Field(..., description="A short summary of the candidate's fit for the role")
    section_scores: List[SectionScore] = Field(default_factory=list, description="Section-wise breakdown scores")
    requirement_matches: List[RequirementMatch] = Field(default_factory=list, description="JD requirement gap analysis")

# These models represent the inputs (which could be pre-parsed)
class CandidateProfile(BaseModel):
    raw_text: str
    
class JobDescription(BaseModel):
    raw_text: str

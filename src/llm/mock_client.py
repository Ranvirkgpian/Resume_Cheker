from src.llm.base import BaseLLMClient
from src.core.models import (
    CandidateProfile, JobDescription, EvaluationResult, EvaluationScores,
    ScoreDimension, TierClassification, SectionScore, RequirementMatch
)

class MockLLMClient(BaseLLMClient):
    def evaluate_candidate(self, candidate: CandidateProfile, jd: JobDescription) -> EvaluationResult:
        """Returns a deterministic, domain-agnostic mock evaluation result."""
        
        is_python = "python" in jd.raw_text.lower()
        is_kafka = "kafka" in jd.raw_text.lower()
        
        overall = 85 if is_python else 60
        tier = TierClassification.TIER_A if overall >= 80 else (TierClassification.TIER_B if overall >= 60 else TierClassification.TIER_C)
        
        sim_explanation = "Candidate has strong AWS Kinesis background which translates well to Kafka." if is_kafka else "Candidate has strong background in related tools which translate well to the required stack."

        return EvaluationResult(
            scores=EvaluationScores(
                exact_match=ScoreDimension(
                    score=overall, 
                    explanation="Matched several core requirements from the JD.",
                    suggestions=[
                        "Add specific version numbers or standards for Core Skill 1 to improve depth",
                        "Include certification names relevant to the JD"
                    ],
                    matched_keywords=["Core Skill 1 (High)", "Core Skill 2 (High)"],
                    missing_keywords=["Missing Tool A", "Missing Framework B"]
                ),
                similarity_match=ScoreDimension(
                    score=overall + 5,
                    explanation=sim_explanation,
                    suggestions=[
                        "Highlight transferable skills more explicitly",
                        "Use terminology that matches the job description exactly"
                    ],
                    matched_keywords=["Related Domain Concept (Medium)"],
                    missing_keywords=["Specific Required Concept"]
                ),
                impact_achievement=ScoreDimension(
                    score=80,
                    explanation="Candidate demonstrated clear outcomes in their last role.",
                    suggestions=[
                        "Add metrics (e.g., 'reduced cost by 15%', 'improved efficiency by 20%')",
                        "Use action verbs like 'optimized', 'designed', 'led'",
                        "Quantify team size and project scope where possible"
                    ],
                    matched_keywords=["Led project", "Improved process"],
                    missing_keywords=["Specific revenue impact", "Scale metrics"]
                ),
                ownership=ScoreDimension(
                    score=75,
                    explanation="Demonstrated good ownership but limited large-scale autonomy.",
                    suggestions=[
                        "Emphasize end-to-end project ownership",
                        "Mention decisions you made independently and their outcomes"
                    ],
                    matched_keywords=["Task owner", "Coordinator"],
                    missing_keywords=["Strategic design", "Stakeholder management"]
                ),
                overall_score=overall
            ),
            tier=tier,
            summary="Mock Evaluation: This is a solid candidate with relevant background, generated via MockClient. Shows strong core skills but needs to tailor the resume closer to the JD's specific tooling.",
            section_scores=[
                SectionScore(
                    section="Education",
                    score=85,
                    explanation="Relevant educational background for the role."
                ),
                SectionScore(
                    section="Experience",
                    score=72,
                    explanation="Relevant experience but roles could better highlight specific tools from the JD."
                ),
                SectionScore(
                    section="Projects",
                    score=78,
                    explanation="Projects show initiative but lack the specific stack required."
                ),
                SectionScore(
                    section="Skills",
                    score=88,
                    explanation="Strong skills section covering most generic requirements."
                ),
            ],
            requirement_matches=[
                RequirementMatch(
                    requirement="Primary Domain Requirement",
                    matched=True,
                    match_percent=90,
                    evidence="Resume mentions significant experience in this area."
                ),
                RequirementMatch(
                    requirement="Secondary Tooling / Software",
                    matched=True,
                    match_percent=70,
                    evidence="Used related tools extensively."
                ),
                RequirementMatch(
                    requirement="Specific Framework / Standard",
                    matched=False,
                    match_percent=10,
                    evidence="No explicit mention in the text."
                )
            ]
        )

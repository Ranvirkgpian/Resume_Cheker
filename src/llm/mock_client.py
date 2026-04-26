from src.llm.base import BaseLLMClient
from src.core.models import (
    CandidateProfile, JobDescription, EvaluationResult, EvaluationScores,
    ScoreDimension, TierClassification, SectionScore, RequirementMatch
)

class MockLLMClient(BaseLLMClient):
    def evaluate_candidate(self, candidate: CandidateProfile, jd: JobDescription) -> EvaluationResult:
        """Returns a deterministic mock evaluation result with all enhanced fields."""
        
        # Simple logic to change mock response based on JD content for demonstration
        is_python = "python" in jd.raw_text.lower()
        is_kafka = "kafka" in jd.raw_text.lower()
        
        overall = 85 if is_python else 60
        tier = TierClassification.TIER_A if overall >= 80 else (TierClassification.TIER_B if overall >= 60 else TierClassification.TIER_C)
        
        sim_explanation = "Candidate has strong AWS Kinesis background which translates well to Kafka." if is_kafka else "Basic semantic overlap."

        return EvaluationResult(
            scores=EvaluationScores(
                exact_match=ScoreDimension(
                    score=overall, 
                    explanation="Matched several core requirements from the JD.",
                    suggestions=[
                        "Add specific version numbers for technologies (e.g., Python 3.11, Django 4.2)",
                        "Include certification names relevant to the JD (e.g., AWS Certified Developer)"
                    ],
                    matched_keywords=["Python", "REST APIs", "SQL", "Git"],
                    missing_keywords=["Docker", "Kubernetes", "CI/CD"]
                ),
                similarity_match=ScoreDimension(
                    score=overall + 5 if overall < 95 else 95,
                    explanation=sim_explanation,
                    suggestions=[
                        "Highlight transferable skills more explicitly (e.g., 'AWS Kinesis experience directly applicable to Kafka streaming')",
                        "Use industry-standard terminology that ATS systems recognize"
                    ],
                    matched_keywords=["Cloud Services", "Streaming", "Microservices"],
                    missing_keywords=["Kafka", "Event-Driven Architecture"]
                ),
                impact_achievement=ScoreDimension(
                    score=80,
                    explanation="Candidate demonstrated clear metrics in their last role.",
                    suggestions=[
                        "Add metrics (e.g., 'reduced cost by 15%', 'improved efficiency by 20%')",
                        "Use action verbs like 'optimized', 'designed', 'led', 'architected'",
                        "Quantify team size and project scope where possible"
                    ],
                    matched_keywords=["Led team", "Reduced latency", "Improved throughput"],
                    missing_keywords=["Revenue impact", "Cost savings", "Scale metrics"]
                ),
                ownership=ScoreDimension(
                    score=75,
                    explanation="Led a small team, showing good ownership but limited large-scale autonomy.",
                    suggestions=[
                        "Emphasize end-to-end project ownership (design → deploy → monitor)",
                        "Mention decisions you made independently and their outcomes",
                        "Highlight mentoring or cross-team collaboration"
                    ],
                    matched_keywords=["Team lead", "Project owner"],
                    missing_keywords=["System design", "Technical strategy", "Stakeholder management"]
                ),
                overall_score=overall
            ),
            tier=tier,
            summary="Mock Evaluation: This is a solid candidate with relevant background, generated via MockClient. The candidate shows strong technical skills with room for improvement in quantifying impact and demonstrating broader ownership.",
            section_scores=[
                SectionScore(
                    section="Education",
                    score=85,
                    explanation="Relevant degree in Computer Science from a recognized institution."
                ),
                SectionScore(
                    section="Experience",
                    score=72,
                    explanation="3+ years of relevant experience but roles could better highlight leadership and scale."
                ),
                SectionScore(
                    section="Projects",
                    score=78,
                    explanation="Personal projects show initiative but lack production-scale complexity."
                ),
                SectionScore(
                    section="Skills",
                    score=88,
                    explanation="Strong technical skills section covering most JD requirements."
                ),
            ],
            requirement_matches=[
                RequirementMatch(
                    requirement="3+ years Python development experience",
                    matched=True,
                    match_percent=90,
                    evidence="Resume mentions 4 years of Python experience across 2 roles."
                ),
                RequirementMatch(
                    requirement="Experience with Kafka or similar streaming platforms",
                    matched=True,
                    match_percent=70,
                    evidence="Used AWS Kinesis extensively (semantically similar to Kafka)."
                ),
                RequirementMatch(
                    requirement="Docker & Kubernetes experience",
                    matched=False,
                    match_percent=10,
                    evidence="No mention of containerization or orchestration tools."
                ),
                RequirementMatch(
                    requirement="CI/CD pipeline experience",
                    matched=False,
                    match_percent=20,
                    evidence="Mentions 'Git' but no CI/CD tooling (Jenkins, GitHub Actions, etc.)."
                ),
                RequirementMatch(
                    requirement="REST API design and development",
                    matched=True,
                    match_percent=95,
                    evidence="Built and maintained multiple REST APIs using Flask and FastAPI."
                ),
            ]
        )

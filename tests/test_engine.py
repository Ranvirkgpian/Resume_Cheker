import pytest
from src.core.models import TierClassification
from src.core.engine import EvaluationEngine
from src.llm.mock_client import MockLLMClient

def test_evaluation_engine_with_mock():
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a Python developer with Kafka experience."
    resume = "I am a software engineer with Python experience. I also used AWS Kinesis extensively."
    
    result = engine.evaluate(resume, jd)
    
    assert result is not None
    assert result.scores.overall_score == 85
    assert result.tier == TierClassification.TIER_A
    assert "Kinesis" in result.scores.similarity_match.explanation

def test_evaluation_engine_poor_fit():
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a C++ developer with RabbitMQ experience."
    resume = "I am a frontend developer using React and CSS."
    
    result = engine.evaluate(resume, jd)
    
    assert result is not None
    assert result.scores.overall_score == 60
    assert result.tier == TierClassification.TIER_B

def test_evaluation_has_suggestions():
    """Feature 1: Verify actionable suggestions are present."""
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a Python developer."
    resume = "Experienced Python developer."
    
    result = engine.evaluate(resume, jd)
    
    assert len(result.scores.exact_match.suggestions) > 0
    assert len(result.scores.impact_achievement.suggestions) > 0
    assert len(result.scores.ownership.suggestions) > 0

def test_evaluation_has_keywords():
    """Feature 2: Verify matched/missing keyword lists are present."""
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a Python developer."
    resume = "Experienced Python developer."
    
    result = engine.evaluate(resume, jd)
    
    assert len(result.scores.exact_match.matched_keywords) > 0
    assert len(result.scores.exact_match.missing_keywords) > 0

def test_evaluation_has_section_scores():
    """Feature 3: Verify section-wise scoring is present."""
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a Python developer."
    resume = "Experienced Python developer."
    
    result = engine.evaluate(resume, jd)
    
    assert len(result.section_scores) == 4
    section_names = [s.section for s in result.section_scores]
    assert "Education" in section_names
    assert "Experience" in section_names
    assert "Projects" in section_names
    assert "Skills" in section_names

def test_evaluation_has_requirement_matches():
    """Feature 4: Verify JD requirement gap analysis is present."""
    client = MockLLMClient()
    engine = EvaluationEngine(client)
    
    jd = "Looking for a Python developer."
    resume = "Experienced Python developer."
    
    result = engine.evaluate(resume, jd)
    
    assert len(result.requirement_matches) > 0
    for req in result.requirement_matches:
        assert isinstance(req.matched, bool)
        assert 0 <= req.match_percent <= 100
        assert len(req.evidence) > 0

from abc import ABC, abstractmethod
from src.core.models import CandidateProfile, JobDescription, EvaluationResult

class BaseLLMClient(ABC):
    @abstractmethod
    def evaluate_candidate(self, candidate: CandidateProfile, jd: JobDescription) -> EvaluationResult:
        """Evaluates a candidate against a job description."""
        pass

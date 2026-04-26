from src.core.models import CandidateProfile, JobDescription, EvaluationResult
from src.llm.base import BaseLLMClient

class EvaluationEngine:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        
    def evaluate(self, resume_text: str, jd_text: str) -> EvaluationResult:
        """
        Orchestrates the evaluation of a resume against a job description.
        In a production scenario, this might publish events or save state.
        """
        candidate = CandidateProfile(raw_text=resume_text)
        jd = JobDescription(raw_text=jd_text)
        
        # Here we could inject pre-processing, text chunking, or verification engine calls
        
        # Call the LLM to perform the heavy lifting of semantic scoring
        result = self.llm_client.evaluate_candidate(candidate, jd)
        
        # Post-processing could be injected here (e.g., overriding tier based on strict rules)
        
        return result

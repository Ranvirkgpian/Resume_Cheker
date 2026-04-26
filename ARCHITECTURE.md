# Architecture Document: AI Resume Shortlisting & Interview Assistant

## Overview

The AI Resume Shortlisting & Interview Assistant System is designed to automate candidate evaluation at scale. It compares incoming candidate resumes against Job Descriptions (JDs), verifies external public claims (e.g., GitHub, LinkedIn), scores candidates across multiple dimensions, and dynamically generates tailored interview questions.

## System Architecture

The end-to-end system comprises four primary engines interacting through an event-driven architecture, enabling scalability and modularity.

1.  **Parsing Engine**: Ingests raw PDFs (resumes) and plain text (JDs). It uses a combination of OCR/PDF-extraction libraries and an initial LLM pass to convert unstructured text into standard, structured JSON representations of candidate profiles.
2.  **Scoring & Evaluation Engine (Implemented)**: The core intelligence layer. It takes the structured candidate profile and the JD as inputs. Using an LLM, it evaluates the candidate across four dimensions:
    *   **Exact Match**: Direct keyword or requirement matches.
    *   **Similarity Match**: Semantic equivalency (e.g., matching AWS Kinesis to Kafka experience).
    *   **Impact/Achievement**: Assessing the depth and scale of achievements (e.g., metrics, business impact).
    *   **Ownership**: Evaluating the candidate's level of responsibility and autonomy.
    It produces a comprehensive evaluation result including scores, tier classification (A, B, C), and human-readable explainability.
3.  **Verification Engine (Future Scope)**: An asynchronous worker that scrapes or calls APIs for linked profiles (GitHub, LinkedIn). It verifies claims (e.g., commit frequency, repository ownership, job history matches) and feeds a "Trust Score" back into the main evaluation.
4.  **Question Generator Engine (Future Scope)**: Uses the tier classification and identified weaknesses/strengths from the Scoring Engine to generate tailored technical and behavioral questions for the human interviewer.

**Data Flow:**
`Raw Resume (PDF)` → `Parsing Engine` → `Structured Profile (JSON)` → `Scoring Engine (with JD)` → `Evaluation Result (Scores + Explanation)` → `Question Generator` → `Interview Packet`.

---

## Data Strategy

**Handling Unstructured PDF Data:**
*   **Extraction:** We use lightweight libraries (e.g., `pypdf` or `pdfplumber`) to extract raw text layers from resumes.
*   **Structuring (LLM-Assisted):** Since resumes follow no standard format, the raw text is passed to a fast, cost-effective LLM (e.g., GPT-4o-mini or Claude 3.5 Haiku) with strict JSON schema enforcement (via structured outputs or function calling). This guarantees a predictable `CandidateProfile` schema containing arrays of `Experience`, `Education`, and `Skills`.
*   **Data Contracts:** All internal services communicate using strictly typed Pydantic models. If a resume is severely malformed, the system falls back to a gracefully degraded "Review Needed" state rather than failing silently.

---

## AI Strategy

**LLM Choices & Reasoning Layer:**
*   **Extraction & Formatting:** GPT-4o-mini is preferred for its low latency, low cost, and excellent JSON adherence.
*   **Deep Reasoning (Scoring Engine):** A highly capable model like GPT-4o or Claude 3.5 Sonnet is required to handle nuanced semantic similarities and multi-dimensional scoring (Ownership, Impact).
*   **Abstract Interface:** The system abstracts LLM calls behind a generic interface (`BaseLLMClient`). This allows seamlessly switching providers (e.g., from OpenAI to Anthropic) and supports a deterministic `MockLLMClient` for local testing and CI without incurring API costs.

**Semantic Similarity:**
While the LLM handles complex contextual matching natively within its context window, a dedicated Embedding/Vector DB approach (e.g., Pinecone + `text-embedding-3-small`) could be layered in for initial screening if JD and Resume sizes grow, or to query past successful candidates. For semantic equivalency (e.g., Kafka vs. RabbitMQ), relying on the LLM's vast pre-trained knowledge base through zero-shot or few-shot prompting provides the most robust and context-aware similarity detection.

---

## Scalability Strategy (10,000+ Resumes/Day)

To process 10,000+ resumes efficiently without hitting rate limits or timeouts, the architecture requires:

1.  **Asynchronous Processing:**
    *   API requests drop the raw resume into an object store (S3) and publish an event to a message broker (e.g., RabbitMQ or AWS SQS).
    *   Stateless worker nodes pull from the queue, process the text extraction, and make the LLM calls asynchronously.
2.  **Rate Limiting & Retries:**
    *   LLM API calls are wrapped in robust retry mechanisms (e.g., `tenacity` in Python) to handle HTTP 429s (Too Many Requests) using exponential backoff.
    *   Batch API endpoints (where supported by the LLM provider) can be used to process large dumps of resumes offline.
3.  **Caching:**
    *   Repeated parsing of the same exact file (verified via SHA-256 hash) immediately returns cached JSON from Redis/Postgres.
4.  **Database & State Management:**
    *   **PostgreSQL** serves as the source of truth for parsed profiles, JDs, and resulting scores.
    *   The system remains stateless at the application layer, allowing horizontal auto-scaling of worker pods based on queue depth.

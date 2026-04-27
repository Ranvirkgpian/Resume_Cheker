# AI Resume Shortlisting & Interview Assistant

> Evaluate candidate resumes against Job Descriptions using AI-powered semantic matching and multi-dimensional scoring.

---

## Features

- **Multi-dimensional Scoring** — evaluates candidates across Exact Match, Similarity Match, Impact & Achievement, and Ownership
- **Explainable AI** — provides written rationale for every score, not just numbers
- **Tier Classification** — automatically sorts candidates into Tier A (Fast-track), Tier B (Technical Screen), or Tier C (Needs Evaluation)
- **JD Gap Analysis** — maps each JD requirement to resume evidence with a per-requirement match percentage
- **Flexible LLM Abstraction** — swap between Mock LLM (no API key), Groq (Llama 3.3 70B), or OpenAI (GPT-4o) at runtime
- **PDF Support** — upload a PDF resume and have text extracted automatically
- **Interactive UI** — clean Streamlit app with progress bars, dataframes, and expandable detail panels

---

## Quick Setup (under 5 minutes)

### Prerequisites

- Python 3.9+
- Git

### macOS

```bash
# 1. Clone the repo
git clone https://github.com/your-org/ai-resume-evaluator.git
cd ai-resume-evaluator

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set API keys
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."

# 5. Run the app
streamlit run src/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. No API key is required if you use **Mock LLM** mode.

---

### VS Code

1. Open the project folder in VS Code: **File → Open Folder**
2. Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) if you haven't already
3. Open the integrated terminal (**Terminal → New Terminal**) and follow the macOS steps above
4. To run with one click, create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Streamlit App",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "src/app.py"],
      "justMyCode": true
    }
  ]
}
```

Then press **F5** to launch.

---

### Antigravity (Replit / cloud IDE)

If you are running this in Antigravity or any hosted Python environment:

1. ```bash
cd "File Path Name"
```
2. In the shell panel, install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m streamlit run src/app.py
```

Antigravity will expose the port automatically. Click the generated URL to open the UI.

---

## Architecture Overview

The system is built around four engines. Only the **Scoring & Evaluation Engine** is fully implemented in this repository; the others are described as future scope in `ARCHITECTURE.md`.

```
Raw Resume (PDF / text)
        │
        ▼
┌───────────────────┐
│   Parsing Engine  │  pypdf extraction → raw text
└────────┬──────────┘
         │ structured text
         ▼
┌──────────────────────────────────────────────┐
│          Scoring & Evaluation Engine         │  ← implemented
│                                              │
│  CandidateProfile ──┐                        │
│  JobDescription  ───┼─► BaseLLMClient ──────►│─► EvaluationResult
│                     │   (Mock / Groq /       │   (scores, tier,
│                     │    OpenAI)             │    summary, gaps)
└──────────────────────────────────────────────┘
         │
         ├──► Verification Engine  (future)
         │    GitHub / LinkedIn claim verification
         │
         └──► Question Generator   (future)
              Tailored interview questions per tier
```

### Key components

| File | Responsibility |
|---|---|
| `src/core/models.py` | Pydantic models — `EvaluationResult`, `ScoreDimension`, `SectionScore`, `RequirementMatch` |
| `src/core/engine.py` | `EvaluationEngine` — thin orchestrator, delegates to LLM client |
| `src/llm/base.py` | `BaseLLMClient` abstract interface |
| `src/llm/mock_client.py` | Deterministic mock, no API call — used for tests and demos |
| `src/llm/openai_client.py` | OpenAI GPT-4o client with JSON-mode enforcement |
| `src/llm/groq_client.py` | Groq Llama-3.3-70B client (OpenAI-compatible SDK) |
| `src/utils/parser.py` | PDF text extraction via `pypdf` |
| `src/app.py` | Streamlit UI |

### Data flow

1. User pastes or uploads a resume; pastes a JD
2. `EvaluationEngine.evaluate()` wraps them in `CandidateProfile` and `JobDescription`
3. The selected `LLMClient.evaluate_candidate()` sends a structured prompt and returns an `EvaluationResult` validated by Pydantic
4. Streamlit renders scores, section breakdown, requirement gap table, and keyword lists

---

## Assumptions and Trade-offs

| Decision | Rationale |
|---|---|
| **Synchronous execution** | Simplifies the demo; a production system would push resumes to a queue (SQS/RabbitMQ) and process asynchronously |
| **Single-prompt evaluation** | Fits resume + JD comfortably in modern context windows (16k+ tokens); avoids multi-turn complexity |
| **LLM for semantic matching** | More robust than hand-crafted keyword rules; avoids the need to maintain custom skill taxonomies |
| **Pydantic for output validation** | Forces the LLM to return well-typed JSON; raises an error rather than silently passing bad data downstream |
| **Mock client for tests** | Enables full CI with no API keys or network calls; mock logic is simple but covers the main scoring paths |
| **Basic PDF extraction** | `pypdf` handles standard text-layer PDFs; scanned or multi-column layouts may require OCR (AWS Textract, Tesseract) |
| **Focus on Option A (Scoring Engine)** | Depth over breadth — a robust evaluation pipeline is more valuable than three half-built engines |

---

## Known Limitations and What's Next

### Current limitations

- PDF extraction fails on scanned or heavily formatted (multi-column, tables) resumes
- The mock client returns static data; it does not actually read the resume or JD
- No persistent storage — results are not saved between sessions
- No batch mode — resumes are processed one at a time
- LLM output quality is sensitive to prompt drift across model versions
- No authentication or rate limiting on the Streamlit UI

### What we would do next

1. **Async queue** — decouple ingestion from evaluation using SQS + worker pods for 10k+ resumes/day
2. **Verification Engine** — async scraper for GitHub commit history and LinkedIn job timelines to produce a "Trust Score"
3. **Question Generator** — use tier + identified gaps to generate tailored technical and behavioral questions per candidate
4. **Structured PDF parsing** — integrate `pdfplumber` or AWS Textract for multi-column and table-heavy resumes
5. **Persistent storage** — PostgreSQL for evaluation results, Redis for deduplication via SHA-256 hash
6. **Embedding-based pre-filter** — use `text-embedding-3-small` + Pinecone to do a fast initial screen before invoking the expensive LLM
7. **Evaluation dashboard** — compare multiple candidates side-by-side for a single JD
8. **Prompt versioning** — pin prompt templates and track output quality across LLM model updates

---

## Sample Dataset / Seed Script

A small set of sample resumes and JDs is included to let you test the pipeline without real candidate data.

### Included samples

```
samples/
  jds/
    senior_python_engineer.txt
    frontend_react_developer.txt
  resumes/
    strong_match_python.txt      # Tier A expected
    partial_match_python.txt     # Tier B expected
    weak_match_frontend.txt      # Tier C expected
```

### Generate synthetic samples

To generate additional synthetic resume/JD pairs for load testing or prompt tuning, run:

```bash
python scripts/generate_samples.py --count 20 --output samples/generated/
```

The script uses the Mock LLM client, so no API key is required. Each generated file is a plain `.txt` with realistic but fictional candidate data.

> If `scripts/generate_samples.py` does not yet exist, copy the template below into that path:

```python
"""Minimal synthetic data generator for testing."""
import random, pathlib, argparse, textwrap

SKILLS = ["Python", "Go", "Kafka", "PostgreSQL", "Docker", "Kubernetes",
          "React", "TypeScript", "AWS", "GCP", "FastAPI", "Django"]
COMPANIES = ["Acme Corp", "Globex", "Initech", "Umbrella Ltd", "Soylent Inc"]

def make_resume(seed: int) -> str:
    random.seed(seed)
    skills = random.sample(SKILLS, 5)
    company = random.choice(COMPANIES)
    yoe = random.randint(2, 10)
    return textwrap.dedent(f"""
        Jane Doe {seed} — Software Engineer
        {yoe} years of experience at {company}.
        Skills: {', '.join(skills)}.
        Led backend services handling 50k req/s.
        Reduced infra cost by 20% via autoscaling.
    """).strip()

def make_jd(seed: int) -> str:
    random.seed(seed + 1000)
    skills = random.sample(SKILLS, 4)
    return textwrap.dedent(f"""
        Senior Engineer — Backend Platform
        We need someone with: {', '.join(skills)}.
        5+ years of experience required.
        Experience with high-throughput distributed systems preferred.
    """).strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--output", default="samples/generated")
    args = parser.parse_args()
    out = pathlib.Path(args.output)
    (out / "resumes").mkdir(parents=True, exist_ok=True)
    (out / "jds").mkdir(parents=True, exist_ok=True)
    for i in range(args.count):
        (out / "resumes" / f"resume_{i:03d}.txt").write_text(make_resume(i))
        (out / "jds" / f"jd_{i:03d}.txt").write_text(make_jd(i))
    print(f"Generated {args.count} resume/JD pairs in {out}/")
```

---

## Running Tests

Tests cover the core engine, domain models, and all four scoring dimensions.

```bash
pytest
```

Expected output:

```
tests/test_engine.py::test_evaluation_engine_with_mock        PASSED
tests/test_engine.py::test_evaluation_engine_poor_fit         PASSED
tests/test_engine.py::test_evaluation_has_suggestions         PASSED
tests/test_engine.py::test_evaluation_has_keywords            PASSED
tests/test_engine.py::test_evaluation_has_section_scores      PASSED
tests/test_engine.py::test_evaluation_has_requirement_matches PASSED

6 passed in 0.11s
```

### What the tests cover

- `test_evaluation_engine_with_mock` — end-to-end happy path: Tier A result, overall score 85, Kinesis-to-Kafka similarity detected
- `test_evaluation_engine_poor_fit` — mismatched JD/resume produces Tier B and score 60
- `test_evaluation_has_suggestions` — all score dimensions return at least one actionable suggestion
- `test_evaluation_has_keywords` — matched and missing keyword lists are both non-empty
- `test_evaluation_has_section_scores` — all four resume sections (Education, Experience, Projects, Skills) are scored
- `test_evaluation_has_requirement_matches` — each JD requirement has a boolean match, a percentage, and evidence text

All tests use `MockLLMClient` — no API key or network access required.

---

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Only for OpenAI mode | GPT-4o evaluation |
| `GROQ_API_KEY` | Only for Groq mode | Llama-3.3-70B evaluation |

Neither variable is required to run the app in **Mock LLM** mode or to run the test suite.

---

## Project Structure

```
.
├── src/
│   ├── app.py                 # Streamlit UI
│   ├── core/
│   │   ├── engine.py          # EvaluationEngine orchestrator
│   │   └── models.py          # Pydantic data models
│   ├── llm/
│   │   ├── base.py            # BaseLLMClient interface
│   │   ├── mock_client.py     # Deterministic mock (no API)
│   │   ├── openai_client.py   # OpenAI GPT-4o client
│   │   └── groq_client.py     # Groq Llama-3.3 client
│   └── utils/
│       └── parser.py          # PDF text extraction
├── tests/
│   └── test_engine.py         # pytest test suite
├── samples/                   # Sample JDs and resumes
├── ARCHITECTURE.md            # Full system design and scalability strategy
├── requirements.txt
└── README.md
```

---

## AI Tools

Using AI effectively is a real skill — here's how it was used in this project.

### What AI was used for

- **Boilerplate generation** — the Pydantic model definitions (`EvaluationResult`, `ScoreDimension`, `SectionScore`, `RequirementMatch`) and the initial Streamlit UI layout were scaffolded with AI assistance, then refined manually
- **Prompt engineering** — the structured JSON prompt inside the OpenAI and Groq clients (the schema description, dimension definitions, and output format instructions) was drafted collaboratively with an AI and iterated on until the LLM returned consistently valid JSON
- **Architecture brainstorming** — the four-engine design (Parsing → Scoring → Verification → Question Generator) and the scalability strategy in `ARCHITECTURE.md` (SQS queues, Redis deduplication, horizontal pod scaling) were explored through back-and-forth with an AI before being written up
- **Test scaffolding** — the initial structure of `tests/test_engine.py` was generated with AI, covering the obvious happy-path and edge-case scenarios

### What was reviewed and changed manually

- **Tier classification thresholds** — the cutoffs (≥80 = Tier A, ≥60 = Tier B) were a product judgment call made manually after reviewing what the mock scores looked like in practice
- **Scoring dimensions** — the choice of four dimensions (Exact Match, Similarity, Impact, Ownership) was a deliberate design decision, not an AI suggestion; alternatives like "Culture Fit" or "Communication" were considered and rejected as too subjective to score reliably
- **Mock client logic** — the `is_python` / `is_kafka` keyword branching in `MockLLMClient` was simplified manually; the AI initially suggested a more elaborate mock that read the actual resume text, which was overkill for a deterministic test fixture
- **LLM abstraction layer** — the `BaseLLMClient` interface and the decision to keep `EvaluationEngine` thin (no business logic, just orchestration) was a manual architectural call to ensure testability and provider flexibility

### One example where we disagreed with the AI's output

The AI initially suggested using **chained LLM calls** — one call to extract structured data from the resume, a second to score it against the JD. The reasoning was that separating parsing from evaluation would improve accuracy and allow each step to be tested independently.

We disagreed and kept it as a **single prompt** for two reasons: first, for the scope of this project the resume and JD fit comfortably within a single context window, so the added latency and cost of two calls was not justified; second, the evaluation dimensions (especially Similarity Match and Ownership) require reading the resume and JD together — splitting them into separate calls would lose the cross-document context that makes the scoring meaningful. The single-prompt approach also made the mock client simpler and the test suite easier to reason about.

---

## Further Reading

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full system design, scalability strategy (10k+ resumes/day), data flow diagrams, and notes on LLM provider choices.

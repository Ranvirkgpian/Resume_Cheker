# AI Resume Shortlisting & Interview Assistant

## Overview

This repository contains the implementation of the **AI Resume Shortlisting & Interview Assistant**. The system evaluates candidate resumes against a provided Job Description (JD) to automatically score the candidate across multiple dimensions, classify them into tiers, and explain the reasoning behind its decisions.

We have focused specifically on **Option A: The Evaluation & Scoring Engine (Core)**, showcasing depth in building robust, explainable AI evaluation pipelines.

For an in-depth view of the system architecture, design decisions, and strategies for scale, please see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Features

- **Multi-dimensional Scoring:** Evaluates candidate profiles based on Exact Match, Similarity Match, Impact & Achievement, and Ownership.
- **Explainable AI:** Does not just return numbers; it provides a written rationale for *why* a candidate received a specific score.
- **Tier Classification:** Automatically sorts candidates into Tier A (Fast-track), Tier B (Technical Screen), or Tier C (Needs Evaluation).
- **Flexible LLM Abstraction:** Comes with an extensible `BaseLLMClient`. By default, you can run a **Mock LLM** (requiring no API keys) or use the **OpenAI Client** for real inference.
- **Interactive UI:** A simple, clean Streamlit application to visually demonstrate the workflow.

---

## Assumptions & Trade-offs

- **Simplification of Parsing:** Real-world resumes are messy. While we have implemented basic PDF text extraction, handling advanced tables or multi-column PDFs perfectly is beyond the 6-10 hour scope. We assume standard, legible text flow.
- **Synchronous Execution for Demo:** For ease of demonstration, the core engine processes the resume synchronously. In a production environment with 10k+ resumes/day, this would be decoupled into asynchronous queues (detailed in `ARCHITECTURE.md`).
- **Focus on Evaluation Engine:** To ensure a robust, high-quality slice of the system, we prioritized the Scoring Engine (Option A) over building out the Verification Engine or Question Generator, ensuring the complex logic of semantic similarity and multi-dimensional scoring works well.
- **LLM Context Limits:** We assume the extracted text of a single resume and JD fits comfortably within modern LLM context windows (e.g., 16k+ tokens).

---

## Setup & Installation

**Prerequisites:** Python 3.9+ 

1. **Clone the repository and navigate to the directory**

2. **Create and activate a virtual environment (optional but recommended)**
   `python3 -m venv venv`
   `source venv/bin/activate`

3. **Install dependencies:**
   `pip install -r requirements.txt`

4. **Environment Variables (Optional):**
   If you intend to use the real OpenAI API, set your API key. If not set, you can still run the app in **Mock Mode**.
   `export OPENAI_API_KEY="your-api-key-here"`

---

## Running the Application

### 1. Launch the Streamlit UI

The easiest way to interact with the system is through the included Streamlit application.

`streamlit run src/app.py`

This will launch a web interface at `http://localhost:8501`. 
- You can paste a Job Description.
- You can either paste Resume text or upload a PDF.
- You can toggle between "Mock LLM" (fast, no API key needed) and "OpenAI" (real evaluation).

### 2. Running Tests

We have included automated tests covering the core logic, domain models, and edge cases.

`pytest`

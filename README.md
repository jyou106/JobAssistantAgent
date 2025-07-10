# Job Assistant Agent

A FastAPI-based backend application that helps job seekers optimize their applications using AI. It analyzes your resume against job descriptions and generates tailored answers to application questions using LLMs from Fireworks AI.

---

## Features

- **Resume Scoring**: Matches your resume against a job posting and gives feedback + a relevance score.
- **Tailored Answer Generation**: Generates specific answers for job application questions based on your resume and the job description.
- **Comprehensive Workflow**: Combines resume scoring and answer generation in one endpoint.

---

## Tech Stack

- **FastAPI** – Web framework for serving API routes.
- **LangChain** – For managing LLM tools and agents.
- **Fireworks AI** – LLM inference API (e.g., LLaMA-v3).
- **Selenium** – For scraping job descriptions dynamically.
- **Pydantic** – For input validation and schema definitions.

## Getting Started

```bash
git clone https://github.com/your-username/JobAssistantAgent.git
cd JobAssistantAgent

pip install -r requirements.txt

FIREWORKS_API_KEY=your_fireworks_key_here

uvicorn app.main:app --reload

Then go to http://127.0.0.1:8000/docs#/
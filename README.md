# InterviewOS — AI Interview Coach

Functional MVP for AI Product Manager and Forward Deployed Engineer interview preparation.

## MVP capabilities
- Resume parsing: PDF, DOCX and TXT
- Resume/job-description alignment analysis
- Role-specific mock interview questions
- Answer evaluation and actionable feedback
- Session summary and downloadable report
- Demo mode without an API key

## Run locally
Create a virtual environment, install backend/requirements.txt, copy .env.example to .env, then run:
uvicorn backend.main:app --reload

Open http://localhost:8000. Add OPENAI_API_KEY to .env to enable model-backed analysis and feedback. Without a key, the app clearly labels deterministic demo output.

## API
GET /health; POST /api/analyze; POST /api/questions; POST /api/evaluate; POST /api/summary.

## Privacy
Uploads are processed in memory and not persisted by this MVP. When AI mode is enabled, extracted resume and job-description text is sent to the configured model provider. Avoid uploading sensitive documents. Never commit secrets.

## Production roadmap
Authentication, PostgreSQL persistence and retention controls, usage limits and billing, observability with PII redaction, CI/CD, security hardening, browser tests, and deployment runbooks.

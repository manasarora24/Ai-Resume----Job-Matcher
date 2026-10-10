# CareerIQ AI

CareerIQ AI is a full-stack career exploration project. It extracts text and a skills profile from PDF and DOCX resumes, lets each signed-in user save job descriptions, and compares profile evidence against job requirements. The score is a deterministic local keyword baseline; it is explainable and useful for exploration, but it is not a validated hiring assessment or an embedding/LLM model.

## Current implementation

- Next.js App Router, strict TypeScript, React, Tailwind CSS 4, Framer Motion, Lucide.
- FastAPI, Pydantic, SQLAlchemy 2, SQLite for local development and PostgreSQL in Compose.
- Argon2 password hashes and expiring signed bearer tokens; account-owned records are checked server-side.
- PDF/DOCX parsing, normalized text, section heuristics, and a configurable maximum upload size.
- Job descriptions, searching, save/unsave, match evidence, and an application status tracker.
- Account deletion cascades through resumes, jobs, saved jobs, and applications.
- No resume text is sent to an external AI provider. OCR, email password reset, OAuth, vector search, and LLM features are not implemented.

## Local development

Requirements: Python 3.11+, Node.js 20+, npm.

1. Copy `.env.example` to `.env`; set `JWT_SECRET` to a random value of at least 32 characters.
2. Start the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. In a second terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

4. Open <http://localhost:3000>. API docs are at <http://localhost:8000/docs>.

SQLite tables are created on API startup for the local prototype. Production schema evolution needs Alembic migrations before deployment; the current repo does not yet include migrations.

## Docker Compose

Set a private `JWT_SECRET` in `.env`, then run `docker compose up --build`. The Compose API uses PostgreSQL and persists the database and uploads in named volumes. Replace the sample database password before exposing the stack to a network. Set `FRONTEND_ORIGINS` to the deployed frontend origin. The frontend API URL is a public build-time setting, not a secret.

## API outline

All `/api` routes except registration and login require `Authorization: Bearer <token>`.

| Area | Routes |
| --- | --- |
| Auth/profile | `POST /api/auth/register`, `POST /api/auth/login`, `GET/DELETE /api/me` |
| Resumes | `GET/POST /api/resumes`, `PATCH/DELETE /api/resumes/{id}` |
| Jobs | `GET/POST /api/jobs`, `POST /api/jobs/{id}/save`, `GET /api/jobs/saved` |
| Matching | `POST /api/matches/{resume_id}/{job_id}` |
| Applications | `GET/POST /api/applications`, `PATCH/DELETE /api/applications/{id}` |
| Dashboard | `GET /api/dashboard` |

## Evaluation

`python evaluation/scripts/evaluate.py` evaluates the deterministic keyword baseline on the versioned synthetic examples and reports Precision@K, Recall@K, and NDCG@K. The tiny synthetic set is a smoke methodology fixture, not evidence of real-world accuracy. See [AI evaluation](docs/ai-evaluation.md). Add human-reviewed, licensed examples before drawing quality conclusions.

## Privacy and security notes

Resume contents are extracted in the API process and stored in the database. Uploaded source bytes are not retained. No external AI provider is called. Users can delete an individual resume or their account. The API checks ownership on resume/job operations and restricts CORS to configured origins. Before production, add rate limiting, CSRF strategy if moving tokens to cookies, Alembic migrations, managed secret rotation, antivirus/quarantine for uploads, encrypted storage/backups, retention controls, and security/dependency scanning. Password reset needs a configured email provider and is not currently provided.

## Limitations and roadmap

This is a functional portfolio foundation, not a claim that every pasted acceptance criterion is complete. Resume parsing is heuristic; heading variations may need correction and the UI currently previews extracted text. The score is skills-overlap plus whether matching skills appear in experience/projects; it does not perform semantic embeddings, experience-year reasoning, or LLM explanation. Job listings are user-entered, not sourced from external job boards. Background processing, OCR, Redis, analytics visualizations, password reset, automated migrations, and frontend component/E2E tests remain future work. Do not use the score to make employment decisions.

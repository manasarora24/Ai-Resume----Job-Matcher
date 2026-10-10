# Architecture

The browser client calls a FastAPI service. FastAPI validates request bodies, resolves the bearer token, and passes account-scoped ORM entities to service functions. SQLAlchemy stores users, resumes, jobs, saved-job links, and application records. SQLite is the no-setup development database; Compose configures PostgreSQL for deployment-shaped local runs.

Resume upload limits bytes before parsing, checks the file signature, and parses PDF/DOCX in-process. Extracted text and heuristic structured fields are stored in the database; raw upload bytes are discarded. The local matching service calculates recognized skill coverage and whether matched terms are present in experience/project text. Weights are 80% coverage and 20% evidence. This is explicitly a keyword baseline, not semantic search or generative AI.

The browser stores the short-lived access token in localStorage for this prototype. Production should move to secure, HttpOnly, SameSite cookies with CSRF protection or use a well-reviewed identity provider. Production changes should include Alembic migration scripts, throttling, and a private object storage strategy if original resume files must be retained.

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import secrets
import jwt
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import User, Resume, Job, SavedJob, Application
from .schemas import Credentials, JobInput, ResumeEdit, ApplicationInput
from .parsing import extract_text, parse_resume
from .matching import score_match

Base.metadata.create_all(bind=engine)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="CareerIQ AI API", version="1.0.0", description="Privacy-aware resume and career matching API. Local matching is a deterministic keyword baseline.")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.frontend_origins.split(",")], allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def user_from_token(auth: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not auth: raise HTTPException(401, "Sign in to continue.")
    try: uid = jwt.decode(auth.credentials, settings.jwt_secret, algorithms=["HS256"]).get("sub")
    except jwt.InvalidTokenError: raise HTTPException(401, "Your session is invalid or expired.")
    user = db.get(User, int(uid)) if uid else None
    if not user: raise HTTPException(401, "Account not found.")
    return user

def token_for(user: User):
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user.id), "exp": exp}, settings.jwt_secret, algorithm="HS256")

def owned(model, item_id: int, user: User, db: Session):
    item = db.scalar(select(model).where(model.id == item_id, model.user_id == user.id))
    if not item: raise HTTPException(404, "Item not found.")
    return item

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/api/auth/register", status_code=201)
def register(body: Credentials, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)): raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, name=body.name.strip() or email.split("@")[0], password_hash=password_hash.hash(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token": token_for(user), "user": {"id": user.id, "email": user.email, "name": user.name}}

@app.post("/api/auth/login")
def login(body: Credentials, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not password_hash.verify(body.password, user.password_hash): raise HTTPException(401, "Email or password is incorrect.")
    return {"token": token_for(user), "user": {"id": user.id, "email": user.email, "name": user.name}}

@app.get("/api/me")
def me(user: User = Depends(user_from_token)):
    return {"id": user.id, "email": user.email, "name": user.name}

@app.delete("/api/me", status_code=204)
def delete_account(user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    db.delete(user); db.commit()

@app.post("/api/resumes", status_code=201)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx"}: raise HTTPException(415, "Upload a PDF or DOCX file.")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, f"Files must be under {settings.max_upload_mb} MB.")
    # Validate signatures before parsing. DOCX is a ZIP container.
    if (suffix == ".pdf" and not data.startswith(b"%PDF-")) or (suffix == ".docx" and not data.startswith(b"PK\x03\x04")):
        raise HTTPException(415, "File content does not match its extension.")
    try: text = extract_text(data, suffix)
    except Exception as exc: raise HTTPException(422, str(exc) if isinstance(exc, ValueError) else "Could not read this document. Please check the file and try again.")
    row = Resume(user_id=user.id, filename=Path(file.filename or "resume" + suffix).name[:255], extracted_text=text, parsed=parse_resume(text))
    db.add(row); db.commit(); db.refresh(row)
    return resume_view(row)

def resume_view(r): return {"id": r.id, "filename": r.filename, "parsed": r.parsed, "preview": r.extracted_text[:2000], "created_at": r.created_at.isoformat()}

@app.get("/api/resumes")
def list_resumes(user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    return [resume_view(r) for r in db.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))]

@app.patch("/api/resumes/{resume_id}")
def edit_resume(resume_id: int, body: ResumeEdit, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    r = owned(Resume, resume_id, user, db); r.parsed = body.parsed; db.commit(); return resume_view(r)

@app.delete("/api/resumes/{resume_id}", status_code=204)
def delete_resume(resume_id: int, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    db.delete(owned(Resume, resume_id, user, db)); db.commit()

@app.post("/api/jobs", status_code=201)
def create_job(body: JobInput, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    from .parsing import SKILLS
    low = body.description.lower()
    job = Job(user_id=user.id, **body.model_dump(), skills=[s for s in SKILLS if re.search(r"(?<![\w+#])" + re.escape(s) + r"(?![\w+#])", low)])
    db.add(job); db.commit(); db.refresh(job); return job_view(job)

def job_view(j): return {"id": j.id, "title": j.title, "company": j.company, "location": j.location, "description": j.description, "skills": j.skills, "created_at": j.created_at.isoformat()}

@app.get("/api/jobs")
def list_jobs(q: str = "", limit: int = 50, offset: int = 0, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    stmt = select(Job).where(Job.user_id == user.id)
    if q.strip(): stmt = stmt.where((Job.title.ilike(f"%{q[:100]}%")) | (Job.company.ilike(f"%{q[:100]}%")) | (Job.description.ilike(f"%{q[:100]}%")))
    return [job_view(j) for j in db.scalars(stmt.order_by(Job.created_at.desc()).offset(max(0, offset)).limit(min(max(1, limit), 100)))]

@app.post("/api/jobs/{job_id}/save")
def save_job(job_id: int, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    owned(Job, job_id, user, db)
    saved = db.scalar(select(SavedJob).where(SavedJob.job_id == job_id, SavedJob.user_id == user.id))
    if saved: db.delete(saved); state = False
    else: db.add(SavedJob(user_id=user.id, job_id=job_id)); state = True
    db.commit(); return {"saved": state}

@app.get("/api/jobs/saved")
def saved_jobs(user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    jobs = db.scalars(select(Job).join(SavedJob, SavedJob.job_id == Job.id).where(SavedJob.user_id == user.id))
    return [job_view(j) for j in jobs]

@app.post("/api/matches/{resume_id}/{job_id}")
def match(resume_id: int, job_id: int, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    resume, job = owned(Resume, resume_id, user, db), owned(Job, job_id, user, db)
    return {"resume_id": resume.id, "job_id": job.id, **score_match(resume.parsed, job.description)}

@app.post("/api/applications", status_code=201)
def create_application(body: ApplicationInput, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    owned(Job, body.job_id, user, db)
    row = Application(user_id=user.id, **body.model_dump()); db.add(row); db.commit(); db.refresh(row); return application_view(row, db)

def application_view(a, db):
    j = db.get(Job, a.job_id)
    return {"id": a.id, "job_id": a.job_id, "title": j.title if j else "Deleted job", "company": j.company if j else "", "status": a.status, "notes": a.notes, "updated_at": a.updated_at.isoformat()}

@app.get("/api/applications")
def applications(user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    return [application_view(a, db) for a in db.scalars(select(Application).where(Application.user_id == user.id).order_by(Application.updated_at.desc()))]

@app.patch("/api/applications/{app_id}")
def update_application(app_id: int, body: ApplicationInput, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    row = owned(Application, app_id, user, db); owned(Job, body.job_id, user, db)
    for k,v in body.model_dump().items(): setattr(row,k,v)
    db.commit(); return application_view(row, db)

@app.delete("/api/applications/{app_id}", status_code=204)
def delete_application(app_id: int, user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    db.delete(owned(Application, app_id, user, db)); db.commit()

@app.get("/api/dashboard")
def dashboard(user: User = Depends(user_from_token), db: Session = Depends(get_db)):
    return {"resume_count": db.scalar(select(func.count()).select_from(Resume).where(Resume.user_id == user.id)), "job_count": db.scalar(select(func.count()).select_from(Job).where(Job.user_id == user.id)), "saved_count": db.scalar(select(func.count()).select_from(SavedJob).where(SavedJob.user_id == user.id)), "application_count": db.scalar(select(func.count()).select_from(Application).where(Application.user_id == user.id))}

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    extracted_text: Mapped[str] = mapped_column(Text)
    parsed: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    owner: Mapped[User] = relationship(back_populates="resumes")

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    company: Mapped[str] = mapped_column(String(180))
    location: Mapped[str] = mapped_column(String(180), default="Remote")
    description: Mapped[str] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    owner: Mapped[User] = relationship(back_populates="jobs")

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)

class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(30), default="Applied")
    notes: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    owner: Mapped[User] = relationship(back_populates="applications")

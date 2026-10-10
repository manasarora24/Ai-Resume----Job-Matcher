import re
from .parsing import SKILLS

def terms(text: str) -> set[str]:
    low = text.lower()
    return {s for s in SKILLS if re.search(r"(?<![\w+#])" + re.escape(s) + r"(?![\w+#])", low)}

def score_match(resume: dict, description: str) -> dict:
    have = set(resume.get("skills", [])) | terms(" ".join(str(v) for v in resume.values()))
    need = terms(description)
    matched, missing = sorted(have & need), sorted(need - have)
    overlap = len(matched) / len(need) if need else 0
    evidence = (resume.get("experience", "") + " " + resume.get("projects", "")).lower()
    evidence_hits = sum(s in evidence for s in matched)
    relevance = evidence_hits / max(1, len(matched))
    # Transparent local baseline; no LLM or embeddings are implied.
    score = round(100 * (0.8 * overlap + 0.2 * relevance))
    return {"score": score, "breakdown": {"skill_coverage": round(overlap * 100), "experience_evidence": round(relevance * 100)}, "matched_skills": matched, "missing_skills": missing, "explanation": f"{len(matched)} of {len(need)} recognized job skills appear in your profile. {evidence_hits} matched skills also appear in your experience or projects."}

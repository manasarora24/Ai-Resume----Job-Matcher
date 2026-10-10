from app.matching import score_match

def test_match_explains_skill_coverage_and_gaps():
    result = score_match({"skills": ["python", "sql"], "experience": "Used Python in projects."}, "Python SQL React")
    assert result["score"] == 63
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["react"]
    assert result["breakdown"]["skill_coverage"] == 67

def test_match_empty_profile_scores_zero():
    result = score_match({}, "Python SQL")
    assert result["score"] == 0
    assert result["missing_skills"] == ["python", "sql"]

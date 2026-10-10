# AI and matching evaluation

## Implemented method

The current scorer is a deterministic, local keyword baseline. Recognized skill coverage is 80% of the score and evidence that matching skills appear in the resume's experience/projects is 20%. It returns the recognized matches and gaps used in that calculation. It does not call an LLM, embed text, or claim semantic understanding.

## Reproduce the fixture

Run `python evaluation/scripts/evaluate.py` from the repository root. `evaluation/datasets/v1.json` contains synthetic profile/job pairs with human-authored relevance labels. The script reports Precision@K, Recall@K, and NDCG@K using the keyword score. The small hand-authored fixture is only a reproducibility check; it cannot support generalization or production accuracy claims.

## Next comparison

For a meaningful comparison, extend the fixture with consented or licensed resumes/job descriptions, multiple reviewers, adjudicated relevance labels, and a documented split. Run identical query/document pairs through (1) lexical keyword overlap, (2) a pinned embedding model with recorded version, and (3) the hybrid ranker. Report metrics and confidence intervals by role family, plus parse skill precision/recall, latency, provider failure rate, and cost. Keep all dataset provenance, licenses, and data handling restrictions with each dataset version.

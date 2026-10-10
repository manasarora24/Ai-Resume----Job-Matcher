import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.matching import score_match

def dcg(values):
    return sum((2**v - 1) / __import__("math").log2(i + 2) for i, v in enumerate(values))

def main():
    dataset = json.loads((ROOT / "evaluation/datasets/v1.json").read_text(encoding="utf-8"))
    p, r, ndcg = [], [], []
    for case in dataset["examples"]:
        ranked = sorted(case["jobs"], key=lambda j: score_match(case["resume"], j["description"])["score"], reverse=True)
        rel = case["relevance"]
        k = min(3, len(ranked)); relevant = sum(v > 0 for v in rel.values())
        gains = [rel.get(j["id"], 0) for j in ranked[:k]]
        p.append(sum(v > 0 for v in gains) / k if k else 0)
        r.append(sum(v > 0 for v in gains) / relevant if relevant else 0)
        ideal = sorted(rel.values(), reverse=True)[:k]
        ndcg.append(dcg(gains) / dcg(ideal) if ideal and dcg(ideal) else 0)
    n = len(p)
    print(f"Dataset {dataset['version']} ({n} synthetic queries; k=3)")
    print(f"Precision@3: {sum(p)/n:.3f}")
    print(f"Recall@3:    {sum(r)/n:.3f}")
    print(f"NDCG@3:      {sum(ndcg)/n:.3f}")
    print("These fixture results do not estimate real-world match quality.")

if __name__ == "__main__": main()

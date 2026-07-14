from recommend import recommend_jobs

ground_truth = {
    101: [201, 211],
    102: [202, 212],
    103: [203],
    108: [208],
    120: [215],
}

def precision_at_k(candidate_id, k=3):
    recommended = recommend_jobs(candidate_id, top_n=k)
    recommended_ids = [r["job_id"] for r in recommended]
    relevant_ids = ground_truth.get(candidate_id, [])
    hits = len(set(recommended_ids) & set(relevant_ids))
    return hits / k

if __name__ == "__main__":
    scores = []
    for cid in ground_truth:
        p = precision_at_k(cid, k=3)
        scores.append(p)
        print(f"Candidate {cid}: Precision@3 = {p:.2f}")
    print(f"\nAverage Precision@3: {sum(scores)/len(scores):.2f}")
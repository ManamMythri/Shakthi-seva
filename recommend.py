import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

candidates_df = pd.read_csv("data/candidates.csv")
jobs_df = pd.read_csv("data/jobs.csv")

def clean_skills(skill_string):
    if pd.isna(skill_string):
        return ""
    skills = re.split(r"[;,]", skill_string.lower())
    return ", ".join([s.strip() for s in skills if s.strip()])

candidates_df["skills_clean"] = candidates_df["skills"].apply(clean_skills)
jobs_df["required_skills_clean"] = jobs_df["required_skills"].apply(clean_skills)

vectorizer = TfidfVectorizer()
all_skills_text = pd.concat([candidates_df["skills_clean"], jobs_df["required_skills_clean"]])
vectorizer.fit(all_skills_text)

candidate_vectors = vectorizer.transform(candidates_df["skills_clean"])
job_vectors = vectorizer.transform(jobs_df["required_skills_clean"])

def recommend_jobs(candidate_id, top_n=5, min_score=0.5):
    matches = candidates_df.index[candidates_df["candidate_id"] == candidate_id]
    if len(matches) == 0:
        raise IndexError("Candidate not found")
    candidate_idx = matches[0]
    candidate_vec = candidate_vectors[candidate_idx]

    similarities = cosine_similarity(candidate_vec, job_vectors).flatten()
    top_indices = np.argsort(similarities)[::-1][:top_n]

    recommendations = jobs_df.iloc[top_indices][["job_id", "title"]].copy()
    recommendations["match_score"] = similarities[top_indices]

    # Only keep jobs with at least 50% similarity
    recommendations = recommendations[recommendations["match_score"] >= min_score]

    return recommendations.to_dict(orient="records")
def skill_gap(candidate_id, job_id):
    candidate_row = candidates_df[candidates_df["candidate_id"] == candidate_id].iloc[0]
    job_row = jobs_df[jobs_df["job_id"] == job_id].iloc[0]

    candidate_skills = set(candidate_row["skills_clean"].split(", "))
    job_skills = set(job_row["required_skills_clean"].split(", "))

    missing = job_skills - candidate_skills
    matched = job_skills & candidate_skills

    return {
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "match_percentage": round(len(matched) / len(job_skills) * 100, 2)
    }
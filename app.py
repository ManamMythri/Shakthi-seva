from flask import Flask, request, jsonify, render_template
from recommend import recommend_jobs, skill_gap

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["GET"])
def get_recommendations():
    candidate_id = request.args.get("candidate_id", type=int)
    top_n = request.args.get("top_n", default=5, type=int)

    if candidate_id is None:
        return jsonify({"error": "candidate_id is required"}), 400

    try:
        results = recommend_jobs(candidate_id, top_n)
        if not results:
            return jsonify({
                "candidate_id": candidate_id,
                "recommendations": [],
                "message": "No strongly matching jobs found (below 50% similarity threshold)."
            })
        return jsonify({"candidate_id": candidate_id, "recommendations": results})
    except IndexError:
        return jsonify({"error": "Candidate not found"}), 404
@app.route("/candidates", methods=["GET"])
def list_candidates():
    from recommend import candidates_df
    return jsonify(candidates_df[["candidate_id", "name", "skills"]].to_dict(orient="records"))

@app.route("/jobs", methods=["GET"])
def list_jobs():
    from recommend import jobs_df
    return jsonify(jobs_df[["job_id", "title", "required_skills"]].to_dict(orient="records"))
@app.route("/skill-gap", methods=["GET"])
def get_skill_gap():
    candidate_id = request.args.get("candidate_id", type=int)
    job_id = request.args.get("job_id", type=int)

    if candidate_id is None or job_id is None:
        return jsonify({"error": "candidate_id and job_id are required"}), 400

    try:
        result = skill_gap(candidate_id, job_id)
        return jsonify(result)
    except (IndexError, KeyError):
        return jsonify({"error": "Candidate or job not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
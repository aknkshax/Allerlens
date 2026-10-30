"""AllerLens backend API (Flask).

Run:   pip install -r requirements.txt && python app.py
Try:   curl -X POST localhost:5000/api/analyze -H 'Content-Type: application/json' \
            -d '{"label":"Wheat flour, milk solids. May contain peanuts.","profile":["peanut","milk"]}'
"""
import random
from flask import Flask, jsonify, request
from analyzer import ALLERGENS, DATA, analyze

app = Flask(__name__)
AA = "ACDEFGHIKLMNPQRSTVWY"


@app.after_request
def cors(resp):  # allow the static front-end to call this API during development
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.get("/api/health")
def health():
    return {"status": "ok", "allergen_groups": len(ALLERGENS), "protein_pages": len(DATA["proteins"])}


@app.get("/api/allergens")
def allergens():
    return jsonify({k: {"name": a["name"], "icon": a["icon"]} for k, a in ALLERGENS.items()})


@app.post("/api/analyze")
def analyze_label():
    body = request.get_json(silent=True) or {}
    result = analyze(body.get("label", ""), body.get("profile", []))
    return jsonify(result), (400 if "error" in result else 200)


@app.get("/api/protein/<key>")
def protein(key):
    p = DATA["proteins"].get(key)
    if not p:
        return jsonify({"error": "not_found", "message": "No protein page for this allergen in the demo set."}), 404
    rng = random.Random(key)  # deterministic DEMO sequence: a placeholder, not a real UniProt record
    return jsonify({**p, "sequence_demo": "".join(rng.choice(AA) for _ in range(90)),
                    "data_status": "DEMO PLACEHOLDER: sequence and epitope ranges are illustrative. Verify record against UniProt/IEDB."})


if __name__ == "__main__":
    app.run(debug=True)

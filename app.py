from flask import Flask, request, jsonify, render_template
import pandas as pd
import re

app = Flask(__name__)

# Load CSV once at startup
df = pd.read_csv("Non-Linear-Bat-Thresholds_FULL.csv")

# Normalize model column
def normalize(value):
    if pd.isna(value):
        return ""
    return re.sub(r'[^A-Z0-9]', '', str(value).upper())

df["MODEL_NORMALIZED"] = df["Model"].apply(normalize)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal error. Please try again."}), 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/")
def home():
    return "Bat Compression Lookup API Running"


@app.route("/lookup")
def lookup():
    model = request.args.get("model", "")
    normalized_model = normalize(model)

    matches = df[df["MODEL_NORMALIZED"] == normalized_model]

    if matches.empty:
        return jsonify({"error": "Model not found"}), 404

    results = matches[[
        "Manufacturer",
        "Model",
        "Description",
        "Barrel Compression Cutoff (psi)",
        "Date Added"
    ]].to_dict(orient="records")

    return jsonify(results)

@app.route("/search")
def search():
    manufacturer = request.args.get("manufacturer", "").strip().lower()
    description = request.args.get("description", "").strip().lower()

    filtered = df.copy()

    if manufacturer:
        filtered = filtered[
            filtered["Manufacturer"].str.lower().str.contains(manufacturer)
        ]

    if description:
        filtered = filtered[
            filtered["Description"].str.lower().str.contains(description)
        ]

    if filtered.empty:
        return jsonify({"error": "No matches found"}), 404

    results = filtered[[
        "Manufacturer",
        "Model",
        "Description",
        "Barrel Compression Cutoff (psi)"
    ]].to_dict(orient="records")

    return jsonify(results)


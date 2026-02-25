from flask import Flask, request, jsonify
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


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
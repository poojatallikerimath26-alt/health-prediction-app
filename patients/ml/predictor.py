"""
predictor.py
------------
Loads the three trained risk-classifier models (once, on first use) and
exposes generate_remarks(), which is the single function the Django view
calls. This is the "AI/ML integration" step required by the task: every
time a patient record is saved, this function runs and the result is
stored in the Remarks field.
"""

import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

_models = {}


def _load_model(name):
    if name not in _models:
        path = os.path.join(MODELS_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model file '{name}' not found. Run "
                f"'python patients/ml/train_model.py' once before starting the server."
            )
        _models[name] = joblib.load(path)
    return _models[name]


def generate_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """
    Runs the three trained models on one patient's readings and returns a
    short, readable remarks string for the Remarks field.
    """
    features = [[glucose, haemoglobin, cholesterol]]

    diabetes_model = _load_model("diabetes_model.pkl")
    anaemia_model = _load_model("anaemia_model.pkl")
    cholesterol_model = _load_model("cholesterol_model.pkl")

    diabetes_risk = diabetes_model.predict(features)[0]
    diabetes_prob = diabetes_model.predict_proba(features)[0][1]

    anaemia_risk = anaemia_model.predict(features)[0]
    anaemia_prob = anaemia_model.predict_proba(features)[0][1]

    chol_risk = cholesterol_model.predict(features)[0]
    chol_prob = cholesterol_model.predict_proba(features)[0][1]

    findings = []

    if diabetes_risk:
        findings.append(f"Elevated glucose suggests possible diabetes risk ({diabetes_prob*100:.0f}% model confidence).")
    else:
        findings.append("Glucose level appears within a normal range.")

    if anaemia_risk:
        findings.append(f"Low haemoglobin suggests possible anaemia risk ({anaemia_prob*100:.0f}% model confidence).")
    else:
        findings.append("Haemoglobin level appears within a normal range.")

    if chol_risk:
        findings.append(f"High cholesterol detected, possible cardiovascular risk ({chol_prob*100:.0f}% model confidence).")
    else:
        findings.append("Cholesterol level appears within a normal range.")

    if not (diabetes_risk or anaemia_risk or chol_risk):
        summary = "No major risk indicators detected. "
    else:
        summary = "Potential health risk(s) detected. Recommend consulting a doctor. "

    return summary + " ".join(findings)

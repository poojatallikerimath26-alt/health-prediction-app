"""
train_model.py
---------------
Builds a small synthetic dataset from standard clinical reference ranges
(glucose, haemoglobin, cholesterol) and trains three separate Logistic
Regression classifiers -- one per risk type:

    1. Diabetes risk        (driven mainly by glucose)
    2. Anaemia risk         (driven mainly by haemoglobin)
    3. High cholesterol risk (driven mainly by cholesterol)

Why synthetic + trained, instead of pure if/else rules?
The task explicitly allows a "custom ML model" instead of a public API
(public health-prediction APIs are mostly paid/unreliable). A trained
model is more defensible as genuine "AI/ML work" than hardcoded
thresholds, while still being explainable: the labels are generated from
real medical reference ranges, with noise added so the model has to
actually learn a decision boundary rather than memorise a rule.

Run with:  python patients/ml/train_model.py
Produces three .pkl files inside patients/ml/models/
"""

import os
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

RNG = np.random.default_rng(42)
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

N_SAMPLES = 4000


def make_dataset():
    # Sample each biomarker from a realistic-ish range.
    glucose = RNG.normal(110, 35, N_SAMPLES).clip(50, 300)
    haemoglobin = RNG.normal(13.5, 2.5, N_SAMPLES).clip(5, 20)
    cholesterol = RNG.normal(190, 45, N_SAMPLES).clip(100, 350)

    # Base label from standard clinical thresholds...
    diabetes_label = (glucose >= 126).astype(int)
    anaemia_label = (haemoglobin < 12).astype(int)
    cholesterol_label = (cholesterol >= 240).astype(int)

    # ...then flip a small percentage of labels at random. This stops the
    # model from being a literal lookup table and forces it to learn a
    # smooth probability boundary near the clinical cutoff, like a real
    # diagnostic model would have to.
    flip_rate = 0.04
    for labels in (diabetes_label, anaemia_label, cholesterol_label):
        flip_idx = RNG.choice(N_SAMPLES, size=int(N_SAMPLES * flip_rate), replace=False)
        labels[flip_idx] = 1 - labels[flip_idx]

    X = np.column_stack([glucose, haemoglobin, cholesterol])
    return X, diabetes_label, anaemia_label, cholesterol_label


def train_and_save():
    X, y_diabetes, y_anaemia, y_chol = make_dataset()

    configs = [
        ("diabetes_model.pkl", y_diabetes, "diabetes risk"),
        ("anaemia_model.pkl", y_anaemia, "anaemia risk"),
        ("cholesterol_model.pkl", y_chol, "high cholesterol risk"),
    ]

    for filename, y, label_name in configs:
        model = LogisticRegression()
        model.fit(X, y)
        path = os.path.join(MODELS_DIR, filename)
        joblib.dump(model, path)
        train_acc = model.score(X, y)
        print(f"Trained {label_name} model -> {filename} (train accuracy: {train_acc:.3f})")


if __name__ == "__main__":
    train_and_save()

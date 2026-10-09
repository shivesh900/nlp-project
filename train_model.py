"""Train, evaluate and export the language-detection model.

Model (unchanged idea from v1): character n-gram TF-IDF (1–3) + Logistic Regression.
Data: data/curated_sentences.csv (the hand-written v1 sentences) +
      data/wikipedia_sentences.csv (real Wikipedia sentences, see scripts/build_dataset.py).

Evaluation is honest: Wikipedia articles are split 80/20 *by article*, so no sentence
from a test article is seen in training. Results go to reports/metrics.json.

Outputs:
  model.pkl, vectorizer.pkl      – used by app.py (Flask) and streamlit_app.py
  web/model.json                 – the same model for the browser demo (frontend/)
  reports/metrics.json           – accuracy, per-language F1, confusion matrix
"""
import json
import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit

from utils.text import clean_text

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
SEED = 42


def load_data():
    curated = pd.read_csv(ROOT / "data" / "curated_sentences.csv")
    curated["article"] = "curated"
    wiki = pd.read_csv(ROOT / "data" / "wikipedia_sentences.csv")
    return curated, wiki


def make_model():
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(1, 3), min_df=2, max_features=20000, dtype=np.float32)
    model = LogisticRegression(class_weight="balanced", max_iter=2000, C=10)
    return vectorizer, model


def first_words(text, n):
    return " ".join(text.split()[:n])


def evaluate(vectorizer, model, test):
    X = vectorizer.transform(test["text"].map(clean_text))
    pred = model.predict(X)
    labels = list(model.classes_)
    report = classification_report(test["language"], pred, labels=labels, output_dict=True, zero_division=0)
    out = {
        "test_sentences": int(len(test)),
        "accuracy": round(accuracy_score(test["language"], pred), 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "per_language_f1": {l: round(report[l]["f1-score"], 4) for l in labels},
        "labels": labels,
        "confusion_matrix": confusion_matrix(test["language"], pred, labels=labels).tolist(),
    }
    for n in (1, 3):
        short = test.assign(text=test["text"].map(lambda t: first_words(t, n)))
        short = short[short["text"].str.len() >= 3]
        p = model.predict(vectorizer.transform(short["text"].map(clean_text)))
        out[f"accuracy_first_{n}_words"] = round(accuracy_score(short["language"], p), 4)
    return out


def v1_baseline(curated, test):
    """The original v1 setup: 3 languages, curated sentences only, raw text at training time."""
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 3))
    clf = LogisticRegression(class_weight="balanced", max_iter=1000)
    clf.fit(vec.fit_transform(curated["text"]), curated["language"])
    sub = test[test["language"].isin(["English", "Tamil", "Hindi"])]
    pred = clf.predict(vec.transform(sub["text"].map(clean_text)))
    return {"languages": 3, "test_sentences": int(len(sub)), "accuracy": round(accuracy_score(sub["language"], pred), 4)}


def export_web(vectorizer, model, path):
    vocab = vectorizer.vocabulary_
    features = [None] * len(vocab)
    for gram, idx in vocab.items():
        features[idx] = gram
    data = {
        "format": "tfidf-char-logreg/v1",
        "ngram_range": list(vectorizer.ngram_range),
        "lowercase": vectorizer.lowercase,
        "classes": list(model.classes_),
        "features": features,
        "idf": [round(float(v), 4) for v in vectorizer.idf_],
        # coef[c][i] for class c and feature i, rounded to keep the file small
        "coef": [[round(float(v), 3) for v in row] for row in model.coef_],
        "intercept": [round(float(v), 4) for v in model.intercept_],
    }
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    log.info(f"web model → {path} ({path.stat().st_size / 1e6:.2f} MB)")


def main():
    curated, wiki = load_data()
    split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    train_idx, test_idx = next(split.split(wiki, groups=wiki["article"]))
    train = pd.concat([curated, wiki.iloc[train_idx]], ignore_index=True)
    test = wiki.iloc[test_idx].reset_index(drop=True)
    log.info(f"train {len(train)} sentences · test {len(test)} sentences from unseen articles · {wiki['language'].nunique()} languages")

    vectorizer, model = make_model()
    model.fit(vectorizer.fit_transform(train["text"].map(clean_text)), train["language"])
    metrics = {"model": "char 1-3 gram TF-IDF (20k features) + LogisticRegression", "held_out": evaluate(vectorizer, model, test)}
    metrics["v1_baseline_on_same_test"] = v1_baseline(curated, test)
    log.info(json.dumps({k: v for k, v in metrics["held_out"].items() if k != "confusion_matrix"}, indent=1))
    log.info(f"v1 baseline: {metrics['v1_baseline_on_same_test']}")

    # Final model: train on everything for the shipped artefacts
    vectorizer, model = make_model()
    full = pd.concat([curated, wiki], ignore_index=True)
    model.fit(vectorizer.fit_transform(full["text"].map(clean_text)), full["language"])
    metrics["shipped_model_trained_on"] = int(len(full))

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (ROOT / "frontend" / "public").mkdir(parents=True, exist_ok=True)
    (ROOT / "frontend" / "public" / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with open(ROOT / "model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(ROOT / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    export_web(vectorizer, model, ROOT / "frontend" / "public" / "model.json")
    log.info("done")


if __name__ == "__main__":
    main()

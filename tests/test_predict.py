"""Tests for the Python model and API (run: pytest -q)."""
import json
from pathlib import Path

import pytest

import utils.predict as P
from utils.text import clean_text

ROOT = Path(__file__).resolve().parent.parent

SAMPLES = {
    "English": "Can you help me finish this machine learning project before Friday?",
    "Tamil": "நான் இன்று கல்லூரிக்கு செல்கிறேன், மாலையில் கிரிக்கெட் விளையாடுவோம்.",
    "Hindi": "मुझे नई भाषाएँ सीखना बहुत पसंद है।",
    "Marathi": "मी उद्या सकाळी पुण्याला जाणार आहे.",
    "Telugu": "ఈ రోజు వాతావరణం చాలా బాగుంది.",
    "Kannada": "ನಾನು ನಾಳೆ ಬೆಂಗಳೂರಿಗೆ ಹೋಗುತ್ತೇನೆ.",
    "Malayalam": "ഞാൻ ഇന്ന് കോളേജിൽ പോകുന്നു.",
    "Bengali": "আমি প্রতিদিন সকালে বই পড়ি।",
    "French": "Je voudrais réserver une table pour deux personnes ce soir.",
    "Spanish": "Me gustaría reservar una mesa para dos personas esta noche.",
    "German": "Ich möchte heute Abend einen Tisch für zwei Personen reservieren.",
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(P, "translate_to_english", lambda text, lang: f"[translated from {lang}]")


def test_clean_text_matches_training():
    assert clean_text("Hello, World!! 123") == "hello world"


@pytest.mark.parametrize("lang,text", SAMPLES.items())
def test_model_predicts_each_language(lang, text):
    pred, conf = P.predict_sentence(text)
    assert pred == lang
    assert conf > 0.6


def test_full_prediction_fields():
    r = P.get_full_prediction("Is this a question?")
    assert r["language"] == "English"
    assert r["sentence_type"] == "Question"
    assert r["complexity"] in {"Easy", "Medium", "Hard", "Too Short"}


@pytest.mark.parametrize("text", ["", "@@@@####$$$$", "xyz bcd fgh"])
def test_unknown_inputs(text):
    assert P.get_full_prediction(text)["language"] == "Unknown"


def test_metrics_are_reported():
    m = json.loads((ROOT / "reports" / "metrics.json").read_text())
    assert m["held_out"]["accuracy"] > 0.95
    assert len(m["held_out"]["labels"]) == 11


def test_flask_api():
    from app import app
    client = app.test_client()
    assert client.get("/health").status_code == 200
    r = client.post("/predict", json={"text": SAMPLES["Tamil"]})
    assert r.status_code == 200 and r.get_json()["language"] == "Tamil"
    assert client.post("/predict", json={}).status_code == 400

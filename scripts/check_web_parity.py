"""Check that the browser model (frontend/src/nlp/model.js + frontend/public/model.json)
gives the same predictions as the Python model (model.pkl + vectorizer.pkl).

Runs the JS model with Node on every sentence of the dataset and compares.
Usage: python scripts/check_web_parity.py
"""
import json
import pickle
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from utils.text import clean_text  # noqa: E402

texts = pd.concat([
    pd.read_csv(ROOT / "data" / "curated_sentences.csv")["text"],
    pd.read_csv(ROOT / "data" / "wikipedia_sentences.csv")["text"],
]).tolist()
texts += ["Hi", "வணக்கம் நண்பா", "क्या हाल है", "Guten Morgen", "¿Dónde está la biblioteca?"]

model = pickle.load(open(ROOT / "model.pkl", "rb"))
vec = pickle.load(open(ROOT / "vectorizer.pkl", "rb"))
py = model.predict_proba(vec.transform([clean_text(t) for t in texts]))

js_code = """
import { LanguageModel, cleanText } from './frontend/src/nlp/model.js';
import fs from 'node:fs';
const m = new LanguageModel(JSON.parse(fs.readFileSync('frontend/public/model.json', 'utf8')));
const texts = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(texts.map(t => { const p = m.predictProba(cleanText(t)); return m.classes.map(c => p[c]); })));
"""
out = subprocess.run(["node", "--input-type=module", "-e", js_code], input=json.dumps(texts), capture_output=True, text=True, cwd=ROOT, check=True)
js = json.loads(out.stdout)

same = sum(int(p.argmax() == max(range(len(j)), key=j.__getitem__)) for p, j in zip(py, js))
max_diff = max(abs(a - b) for p, j in zip(py, js) for a, b in zip(p, j))
print(f"{same}/{len(texts)} identical predictions · max probability difference {max_diff:.4f}")
sys.exit(0 if same == len(texts) and max_diff < 0.02 else 1)

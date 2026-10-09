// Browser inference for the scikit-learn model exported by train_model.py.
// Re-implements TfidfVectorizer(analyzer="char", ngram_range=(1,3)) + LogisticRegression
// exactly, so the browser gives the same probabilities as Python (checked by
// scripts/check_web_parity.py).

/** Same normalisation as utils/text.py → clean_text(). */
export function cleanText(text) {
  return text
    .replace(/[!@#$(),\n"%^*?:;~0-9]/g, " ")
    .replace(/\[\]/g, " ")
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
}

export class LanguageModel {
  constructor(data) {
    if (data.format !== "tfidf-char-logreg/v1") throw new Error("Unknown model format");
    this.classes = data.classes;
    this.idf = Float32Array.from(data.idf);
    this.coef = data.coef.map((row) => Float32Array.from(row));
    this.intercept = data.intercept;
    this.minN = data.ngram_range[0];
    this.maxN = data.ngram_range[1];
    this.lowercase = data.lowercase;
    this.index = new Map(data.features.map((f, i) => [f, i]));
  }

  static async load(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Couldn't load the model (${res.status})`);
    return new LanguageModel(await res.json());
  }

  /** sklearn's _char_ngrams: collapse runs of whitespace, then all n-grams by code point. */
  ngrams(text) {
    let doc = this.lowercase ? text.toLowerCase() : text;
    doc = doc.replace(/\s\s+/g, " ");
    const chars = Array.from(doc);
    const counts = new Map();
    for (let n = this.minN; n <= Math.min(this.maxN, chars.length); n++) {
      for (let i = 0; i + n <= chars.length; i++) {
        const idx = this.index.get(chars.slice(i, i + n).join(""));
        if (idx !== undefined) counts.set(idx, (counts.get(idx) || 0) + 1);
      }
    }
    return counts;
  }

  /** Probabilities per class for already-cleaned text (softmax over the logits). */
  predictProba(cleaned) {
    const counts = this.ngrams(cleaned);
    const x = [];
    let norm = 0;
    for (const [idx, tf] of counts) {
      const v = tf * this.idf[idx];
      x.push([idx, v]);
      norm += v * v;
    }
    norm = Math.sqrt(norm) || 1;
    const logits = this.coef.map((w, c) => {
      let s = this.intercept[c];
      for (const [idx, v] of x) s += w[idx] * (v / norm);
      return s;
    });
    const max = Math.max(...logits);
    const exps = logits.map((l) => Math.exp(l - max));
    const sum = exps.reduce((a, b) => a + b, 0);
    return Object.fromEntries(this.classes.map((c, i) => [c, exps[i] / sum]));
  }

  predict(text) {
    const cleaned = cleanText(text);
    if (!cleaned) return { language: "Unknown", confidence: 0, probabilities: {} };
    const probabilities = this.predictProba(cleaned);
    const [language, confidence] = Object.entries(probabilities).sort((a, b) => b[1] - a[1])[0];
    return { language, confidence, probabilities };
  }
}

// Port of utils/predict.py (v1) to the browser: gibberish check, thresholds,
// word-level detection, sentence type, Flesch reading ease and translation.
import { cleanText } from "./model.js";

export const LANG_CODES = {
  English: "en", Hindi: "hi", Tamil: "ta", Telugu: "te", Kannada: "kn", Malayalam: "ml",
  Bengali: "bn", Marathi: "mr", French: "fr", Spanish: "es", German: "de",
};

export function isGibberish(text) {
  const latin = text.toLowerCase().match(/[a-z]/g);
  if (latin && !/[aeiou]/i.test(text)) return true; // Latin letters but no vowels: "xyz bcd"
  return false;
}

export function sentenceType(text) {
  const t = text.trim();
  if (!t) return "Unknown";
  if (/[?？]$/.test(t)) return "Question";
  if (/[!！]$/.test(t)) return "Exclamation";
  return "Statement";
}

// Syllable estimate for English (vowel groups, silent e, -le endings), like textstat.
export function syllables(word) {
  const w = word.toLowerCase().replace(/[^a-z]/g, "");
  if (!w) return 0;
  if (w.length <= 3) return 1;
  const stripped = w.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, "").replace(/^y/, "");
  const groups = stripped.match(/[aeiouy]{1,2}/g);
  return Math.max(1, groups ? groups.length : 1);
}

export function fleschReadingEase(text) {
  const words = text.match(/[A-Za-z]+(?:'[A-Za-z]+)?/g) || [];
  const sentences = Math.max(1, (text.match(/[.!?]+(\s|$)/g) || []).length);
  if (!words.length) return null;
  const syl = words.reduce((s, w) => s + syllables(w), 0);
  return 206.835 - 1.015 * (words.length / sentences) - 84.6 * (syl / words.length);
}

export function complexity(text, language) {
  if (text.trim().split(/\s+/).length < 3) return { score: 0, level: "Too Short", note: "N/A" };
  if (language !== "English") return { score: null, level: "N/A", note: "Readability scoring is for English text" };
  const score = fleschReadingEase(text);
  const level = score >= 60 ? "Easy" : score >= 30 ? "Medium" : "Hard";
  return { score: Math.round(score * 100) / 100, level, note: "Flesch Reading Ease (higher = easier)" };
}

export function wordLevel(model, text) {
  return text
    .split(/\s+/)
    .filter((w) => Array.from(w).length > 2 && /\p{L}/u.test(w))
    .map((w) => {
      const cleaned = cleanText(w);
      if (!cleaned) return null;
      const probs = model.predictProba(cleaned);
      const [language, confidence] = Object.entries(probs).sort((a, b) => b[1] - a[1])[0];
      return { word: w, language, confidence };
    })
    .filter(Boolean);
}

/** Same decision rules as v1's get_full_prediction (minus the server-only langdetect fallback). */
export function analyse(model, text) {
  const base = { language: "Unknown", confidence: 0, probabilities: {}, wordLevel: [], sentenceType: sentenceType(text) };
  if (!text || !text.trim()) return { ...base, source: "empty" };
  if (!/\p{L}/u.test(text)) return { ...base, source: "no_letters" };
  if (isGibberish(text)) return { ...base, source: "gibberish_check" };

  const { language, confidence, probabilities } = model.predict(text);
  const words = text.trim().split(/\s+/).length;
  const unsure = confidence < 0.6 || (words < 2 && confidence < 0.9);
  const lang = unsure ? "Unknown" : language;
  return {
    language: lang,
    best_guess: language,
    confidence,
    probabilities,
    source: "ml_model",
    wordLevel: wordLevel(model, text),
    sentenceType: sentenceType(text),
    complexity: complexity(text, lang),
  };
}

async function getJSON(url, timeoutMs = 10000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(url, { signal: ctrl.signal });
    if (!r.ok) throw new Error(`${r.status}`);
    return await r.json();
  } finally {
    clearTimeout(t);
  }
}

/** Translate to English: Google's public endpoint, with MyMemory as a fallback. */
export async function translateToEnglish(text, language) {
  const src = LANG_CODES[language] || "auto";
  if (src === "en") return { text, provider: "none" };
  try {
    const d = await getJSON(
      `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=en&dt=t&q=${encodeURIComponent(text)}`
    );
    const out = (d[0] || []).map((p) => p[0]).join("");
    if (out) return { text: out, provider: "Google Translate" };
  } catch {
    /* fall through */
  }
  const d = await getJSON(
    `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text.slice(0, 480))}&langpair=${src === "auto" ? "autodetect" : src}|en`
  );
  return { text: d.responseData?.translatedText || "Translation unavailable.", provider: "MyMemory" };
}

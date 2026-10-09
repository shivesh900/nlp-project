import React, { useEffect, useMemo, useState } from 'react';
import { LanguageModel } from '../nlp/model.js';
import { analyse, translateToEnglish } from '../nlp/analysis.js';

const BASE = import.meta.env.BASE_URL;

const EXAMPLES = [
  { label: 'English', text: 'Can you help me finish this machine learning project before Friday?' },
  { label: 'தமிழ்', text: 'நான் இன்று கல்லூரிக்கு செல்கிறேன், மாலையில் கிரிக்கெட் விளையாடுவோம்.' },
  { label: 'हिन्दी', text: 'मुझे नई भाषाएँ सीखना बहुत पसंद है।' },
  { label: 'मराठी', text: 'मी उद्या सकाळी पुण्याला जाणार आहे.' },
  { label: 'తెలుగు', text: 'ఈ రోజు వాతావరణం చాలా బాగుంది.' },
  { label: 'Français', text: 'Je voudrais réserver une table pour deux personnes ce soir.' },
  { label: 'Mixed', text: 'Hello நண்பா, आज का plan क्या है?' },
];

const LanguageDetector = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [translation, setTranslation] = useState(null);
  const [model, setModel] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    LanguageModel.load(`${BASE}model.json`).then(setModel).catch((e) => setError(e.message));
    fetch(`${BASE}metrics.json`).then((r) => (r.ok ? r.json() : null)).then(setMetrics).catch(() => {});
  }, []);

  const handleSubmit = async (value = text) => {
    if (!value.trim()) {
      setError('Please enter some text to detect.');
      return;
    }
    if (!model) return;
    setLoading(true);
    setError('');
    setTranslation(null);
    const t0 = performance.now();
    const r = analyse(model, value);
    r.ms = Math.max(1, Math.round(performance.now() - t0));
    setResult(r);
    setLoading(false);
    if (r.language !== 'Unknown' && r.language !== 'English') {
      setTranslation({ pending: true });
      try {
        setTranslation(await translateToEnglish(value, r.language));
      } catch {
        setTranslation({ text: 'Translation service unavailable right now.', provider: null });
      }
    }
  };

  const top = useMemo(
    () => (result ? Object.entries(result.probabilities).sort((a, b) => b[1] - a[1]).slice(0, 5) : []),
    [result]
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 font-sans">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <header className="mb-8 text-center">
          <h1 className="text-3xl md:text-5xl font-extrabold mb-4">
            <span aria-hidden="true">🌍 </span>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">NLP Language Detection System</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400">
            Detect 11 languages, analyse sentences and translate — the ML model runs right in your browser
          </p>
        </header>

        {/* Input Card */}
        <div className="bg-gray-800 p-5 sm:p-8 rounded-2xl shadow-2xl mb-8 border border-gray-700/50 hover:border-blue-500/30 transition-colors duration-300">
          <label htmlFor="text" className="sr-only">Text to analyse</label>
          <textarea
            id="text"
            className="w-full h-40 sm:h-48 p-4 rounded-xl bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-lg placeholder-gray-600 resize-none"
            placeholder="Type or paste text… (English, Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Marathi, French, Spanish, German)"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="mt-3 flex flex-wrap gap-2" aria-label="Examples">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                onClick={() => { setText(ex.text); handleSubmit(ex.text); }}
                className="px-3 py-1.5 rounded-lg bg-gray-700/60 hover:bg-gray-600 text-sm text-gray-200 transition-colors"
              >
                {ex.label}
              </button>
            ))}
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={() => handleSubmit()}
              disabled={loading || !model}
              data-testid="analyze"
              className={`flex-1 p-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-3 ${
                loading || !model ? 'bg-blue-800 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]'
              }`}
            >
              {!model ? 'Loading model…' : loading ? 'Analyzing...' : <>🚀 Analyze Text</>}
            </button>

            <button
              onClick={() => { setText(''); setResult(null); setError(''); setTranslation(null); }}
              className="px-6 rounded-xl bg-gray-700 hover:bg-gray-600 text-gray-300 font-semibold transition-colors"
            >
              Clear
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-500/30 text-red-400 rounded-xl">{error}</div>
          )}
        </div>

        {/* Results Section */}
        {result && (
          <div data-testid="result">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Language</p>
                <p className="text-xl sm:text-2xl font-black mt-1" data-testid="language">{result.language}</p>
                {result.language === 'Unknown' && result.best_guess && (
                  <p className="text-xs text-gray-500 mt-1">best guess: {result.best_guess}</p>
                )}
              </div>
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Confidence</p>
                <p className="text-xl sm:text-2xl font-black mt-1">{(result.confidence * 100).toFixed(2)}%</p>
              </div>
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Complexity</p>
                <span className={`inline-block px-4 py-1.5 rounded-lg font-bold text-sm ${
                  result.complexity?.level === 'Easy' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                  result.complexity?.level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                  result.complexity?.level === 'Hard' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                  'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                }`}>
                  {result.complexity?.level || 'N/A'}
                </span>
              </div>
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Sentence Type</p>
                <p className="text-xl sm:text-2xl font-bold mt-1 break-words">{result.sentenceType}</p>
              </div>
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Readability</p>
                <p className="text-xl sm:text-2xl font-bold mt-1 break-words">{result.complexity?.score ?? '—'}</p>
                <p className="text-xs text-gray-500 mt-1">{result.complexity?.note}</p>
              </div>
              <div className="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Inference</p>
                <p className="text-xl sm:text-2xl font-bold mt-1 break-words">{result.ms} ms</p>
                <p className="text-xs text-gray-500 mt-1">in your browser, no server</p>
              </div>
            </div>

            {top.length > 0 && (
              <div className="bg-gray-800 p-5 sm:p-8 rounded-2xl border border-gray-700 mt-6 shadow-2xl">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-4">Model probabilities</p>
                <div className="space-y-2">
                  {top.map(([lang, p]) => (
                    <div key={lang} className="flex items-center gap-3 text-sm">
                      <span className="w-24 shrink-0 text-gray-300">{lang}</span>
                      <div className="flex-1 h-2.5 bg-gray-900 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-500 to-teal-400 rounded-full" style={{ width: `${(p * 100).toFixed(1)}%` }} />
                      </div>
                      <span className="w-16 text-right tabular-nums text-gray-400">{(p * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {translation && (
              <div className="bg-gray-800 p-5 sm:p-8 rounded-2xl border border-gray-700 mt-6 shadow-2xl" data-testid="translation">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-3">English Translation</p>
                <p className="text-xl italic text-blue-100/90 leading-relaxed">
                  {translation.pending ? 'Translating…' : `"${translation.text}"`}
                </p>
                {translation.provider && <p className="text-xs text-gray-500 mt-2">via {translation.provider}</p>}
              </div>
            )}

            {result.wordLevel.length > 0 && (
              <div className="mt-8">
                <p className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-1 bg-blue-600 rounded-full" />
                  Word Breakdown
                </p>
                <div className="flex flex-wrap gap-3">
                  {result.wordLevel.map((item, index) => (
                    <div key={index} className="bg-blue-600/10 border border-blue-500/30 hover:bg-blue-600 hover:text-white px-4 py-2 rounded-xl transition-all duration-200 cursor-default group">
                      <span className="font-bold">{item.word}</span>
                      <span className="ml-2 text-xs opacity-60 group-hover:opacity-100">({item.language})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {metrics && (
          <div className="mt-10 text-sm text-gray-400 bg-gray-800/50 border border-gray-700/50 rounded-2xl p-5">
            <p className="font-semibold text-gray-300 mb-1">About the model</p>
            <p>
              Character 1–3-gram TF-IDF + Logistic Regression (scikit-learn), exported to JSON and run in JavaScript.
              On {metrics.held_out.test_sentences} held-out Wikipedia sentences from articles it never saw:
              <strong className="text-gray-200"> {(metrics.held_out.accuracy * 100).toFixed(1)}% accuracy</strong>,
              macro-F1 {(metrics.held_out.macro_f1 * 100).toFixed(1)}%; on just the first 3 words of each sentence,
              {' '}{(metrics.held_out.accuracy_first_3_words * 100).toFixed(1)}%.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LanguageDetector;

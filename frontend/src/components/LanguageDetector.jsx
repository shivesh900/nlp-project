import React, { useState } from 'react';
import axios from 'axios';

const LanguageDetector = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/predict';

  const handleSubmit = async () => {
    if (!text.trim()) {
      setError('Please enter some text to detect.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(API_URL, { text });
      setResult(response.data);
    } catch (err) {
      console.error('API Error:', err);
      setError(err.response?.data?.message || 'Failed to detect language. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 font-sans">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <header className="mb-10 text-center animate-in fade-in slide-in-from-top-4 duration-700">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
            🌍 NLP Language Detection System
          </h1>
          <p className="text-xl text-gray-400">
            Detect language, analyze complexity, and translate text
          </p>
        </header>

        {/* Input Card */}
        <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl mb-8 border border-gray-700/50 backdrop-blur-sm hover:border-blue-500/30 transition-colors duration-300">
          <textarea
            className="w-full h-48 p-4 rounded-xl bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-lg placeholder-gray-600 resize-none"
            placeholder="Enter your text here... (English, Tamil, Hindi, or Mixed)"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSubmit}
              disabled={loading}
              className={`flex-1 p-4 rounded-xl font-bold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3 ${
                loading ? 'bg-blue-800 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]'
              }`}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Analyzing...</span>
                </div>
              ) : (
                <>🚀 Analyze Text</>
              )}
            </button>
            
            <button 
              onClick={() => { setText(''); setResult(null); setError(''); }}
              className="px-6 rounded-xl bg-gray-700 hover:bg-gray-600 text-gray-300 font-semibold transition-colors"
            >
              Clear
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-500/30 text-red-400 rounded-xl animate-in shake duration-500">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              {/* Language Card */}
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:scale-105 hover:border-blue-500/50 transition-all duration-300 shadow-xl group">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider group-hover:text-blue-400 transition-colors">Language</p>
                <p className="text-2xl font-black mt-1">{result.language}</p>
              </div>

              {/* Confidence Card */}
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:scale-105 hover:border-teal-500/50 transition-all duration-300 shadow-xl group">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider group-hover:text-teal-400 transition-colors">Confidence</p>
                <p className="text-2xl font-black mt-1">
                  {(result.confidence * 100).toFixed(2)}%
                </p>
              </div>

              {/* Complexity Card */}
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:scale-105 hover:border-purple-500/50 transition-all duration-300 shadow-xl group">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider group-hover:text-purple-400 transition-colors mb-2">Complexity</p>
                <span className={`inline-block px-4 py-1.5 rounded-lg font-bold text-sm shadow-inner ${
                  result.complexity === "Easy" ? "bg-green-500/20 text-green-400 border border-green-500/30" :
                  result.complexity === "Medium" ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30" :
                  "bg-red-500/20 text-red-400 border border-red-500/30"
                }`}>
                  {result.complexity}
                </span>
              </div>

              {/* Sentence Type Card */}
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:scale-105 hover:border-indigo-500/50 transition-all duration-300 shadow-xl group">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider group-hover:text-indigo-400 transition-colors">Sentence Type</p>
                <p className="text-2xl font-bold mt-1">{result.sentence_type}</p>
              </div>

              {/* Readability Card */}
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:scale-105 hover:border-pink-500/50 transition-all duration-300 shadow-xl group">
                <p className="text-gray-400 text-sm font-medium uppercase tracking-wider group-hover:text-pink-400 transition-colors">Readability</p>
                <p className="text-2xl font-bold mt-1">{result.readability_score}</p>
              </div>
            </div>

            {/* Translation Section */}
            <div className="bg-gray-800 p-8 rounded-2xl border border-gray-700 mt-8 shadow-2xl hover:border-blue-500/30 transition-colors">
              <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-3">English Translation</p>
              <p className="text-xl italic text-blue-100/90 leading-relaxed">"{result.translation}"</p>
            </div>

            {/* Word-Level Breakdown */}
            <div className="mt-10">
              <p className="text-2xl font-bold mb-4 flex items-center gap-2">
                <span className="w-8 h-1 bg-blue-600 rounded-full" />
                Word Breakdown
              </p>
              <div className="flex flex-wrap gap-3">
                {result.word_level.map((item, index) => (
                  <div
                    key={index}
                    className="bg-blue-600/10 border border-blue-500/30 hover:bg-blue-600 hover:text-white px-4 py-2 rounded-xl transition-all duration-200 cursor-default group"
                  >
                    <span className="font-bold">{item.word}</span>
                    <span className="ml-2 text-xs opacity-60 group-hover:opacity-100">({item.language})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LanguageDetector;

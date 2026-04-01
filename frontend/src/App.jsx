import React from 'react';
import LanguageDetector from './components/LanguageDetector';

function App() {
  return (
    <main className="min-h-screen bg-slate-950 py-12 px-4 selection:bg-primary-500/30">
      <LanguageDetector />
      
      <footer className="mt-12 text-center text-gray-600 text-sm">
        <p>© 2026 NLP Language Detection System. Powered by Scikit-Learn & GoogleTrans.</p>
      </footer>
    </main>
  );
}

export default App;

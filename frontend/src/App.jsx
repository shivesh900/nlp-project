import React from 'react';
import LanguageDetector from './components/LanguageDetector';

function App() {
  return (
    <main className="min-h-screen bg-slate-950 py-12 px-4 selection:bg-primary-500/30">
      <LanguageDetector />
      
      <footer className="mt-12 text-center text-gray-600 text-sm">
        <p>© 2026 NLP Language Detection System. Built by Shivesh Haran P · scikit-learn model running in the browser · <a className="underline" href="https://github.com/shivesh900/nlp-project">source</a></p>
      </footer>
    </main>
  );
}

export default App;

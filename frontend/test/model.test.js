import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { LanguageModel, cleanText } from '../src/nlp/model.js';
import { analyse, sentenceType, isGibberish, fleschReadingEase } from '../src/nlp/analysis.js';

const model = new LanguageModel(JSON.parse(fs.readFileSync(new URL('../public/model.json', import.meta.url), 'utf8')));

test('detects languages in the browser model', () => {
  const cases = {
    English: 'Can you help me finish this project before Friday?',
    Tamil: 'நான் இன்று கல்லூரிக்கு செல்கிறேன்.',
    Hindi: 'मुझे नई भाषाएँ सीखना बहुत पसंद है।',
    Marathi: 'मी उद्या सकाळी पुण्याला जाणार आहे.',
    German: 'Ich möchte heute Abend einen Tisch reservieren.',
  };
  for (const [lang, text] of Object.entries(cases)) assert.equal(analyse(model, text).language, lang, text);
});

test('unknown for empty, symbols and noise; sentence types', () => {
  assert.equal(analyse(model, '').language, 'Unknown');
  assert.equal(analyse(model, '@@@@####').language, 'Unknown');
  assert.equal(isGibberish('xyz bcd'), true);
  assert.equal(sentenceType('Is this a question?'), 'Question');
  assert.equal(sentenceType('Wow!'), 'Exclamation');
});

test('clean text and readability', () => {
  assert.equal(cleanText('Hello, World!! 123'), 'hello world');
  assert.ok(fleschReadingEase('This is a simple sentence.') > 60);
  assert.ok(fleschReadingEase('The juxtaposition of paradigms within contemporary linguistic frameworks remains a subject of considerable debate.') < 30);
});

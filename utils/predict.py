import pickle
import os
import re
import logging
from googletrans import Translator
from langdetect import detect, detect_langs
import textstat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Translator
translator = Translator()

# Singleton for model and vectorizer
_model = None
_vectorizer = None

def load_resources():
    """
    Singleton loader for model and vectorizer.
    """
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')
        VEC_PATH = os.path.join(BASE_DIR, 'vectorizer.pkl')
        
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
                with open(MODEL_PATH, 'rb') as f:
                    _model = pickle.load(f)
                with open(VEC_PATH, 'rb') as f:
                    _vectorizer = pickle.load(f)
                logger.info("ML Resources loaded successfully.")
            else:
                logger.warning("ML Model files not found.")
        except Exception as e:
            logger.error(f"Error loading resources: {e}")
            _model, _vectorizer = None, None
            
    return _model, _vectorizer

def clean_text(text):
    """
    Normalized cleaning.
    """
    text = re.sub(r'[!@#$(),\n"%^*?\:;~0-9]', ' ', text)
    text = re.sub(r'\[\]', ' ', text)
    text = text.lower()
    return ' '.join(text.split())

def is_gibberish(text):
    """
    Heuristic check for gibberish (e.g. 'xyz abc def').
    Checks for vowel presence in long sequences.
    """
    # If no vowels are found in a string containing 'a-z'
    if any(c.isalpha() for c in text):
        # Basic check for English/Latin based gibberish (no vowels)
        latin_chars = re.findall(r'[a-z]', text.lower())
        if latin_chars:
            vowels = re.findall(r'[aeiou]', text.lower())
            if not vowels:
                return True
    return False

def detect_external(text):
    """
    Fallback detection using langdetect.
    """
    try:
        lang_code = detect(text)
        probs = detect_langs(text)
        confidence = round(probs[0].prob, 4)
        
        mapping = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi'}
        return mapping.get(lang_code, lang_code.upper()), confidence
    except:
        return "Unknown", 0.0

def predict_sentence(text):
    """
    Primary prediction using custom ML model.
    """
    model, vectorizer = load_resources()
    if not model or not vectorizer:
        return "Unknown", 0.0
    
    cleaned = clean_text(text)
    if not cleaned:
        return "Unknown", 0.0
        
    vec = vectorizer.transform([cleaned])
    probs = model.predict_proba(vec)[0]
    confidence = round(max(probs), 4)
    prediction = model.classes_[probs.argmax()]
    return prediction, confidence

def predict_word_level(text):
    """
    Word-level analysis with strict filtering.
    """
    model, vectorizer = load_resources()
    if not model or not vectorizer:
        return []
        
    words = text.split()
    results = []
    
    for word in words:
        if len(word) <= 2 or not any(c.isalpha() for c in word):
            continue
            
        cleaned_word = clean_text(word)
        if not cleaned_word:
            continue
            
        try:
            vec = vectorizer.transform([cleaned_word])
            probs = model.predict_proba(vec)[0]
            lang = model.classes_[probs.argmax()]
            results.append({"word": word, "language": lang})
        except:
            continue
    return results

def translate_to_english(text, src_lang):
    """
    Translation logic.
    """
    try:
        lang_map = {'English': 'en', 'Tamil': 'ta', 'Hindi': 'hi'}
        src_code = lang_map.get(src_lang, 'auto')
        translation = translator.translate(text, dest='en', src=src_code)
        return translation.text
    except Exception as e:
        return "Translation unavailable."

def analyze_complexity(text):
    """
    Analyzes text complexity using Flesch Reading Ease.
    """
    try:
        # Edge Case: Short Text
        if len(text.split()) < 3:
            return 0, "Too Short"

        score = textstat.flesch_reading_ease(text)

        if score >= 60:
            level = "Easy"
        elif score >= 30:
            level = "Medium"
        else:
            level = "Hard"

        return round(score, 2), level

    except Exception:
        return 0, "Unknown"

def detect_sentence_type(text):
    """
    Classifies sentence type based on ending punctuation.
    """
    text = text.strip()
    if not text:
        return "Unknown"
    if text.endswith("?"):
        return "Question"
    elif text.endswith("!"):
        return "Exclamation"
    else:
        return "Statement"

def get_full_prediction(text):
    """
    Unified entry point with Anti-Gibberish and smart fallback.
    """
    if not text or not text.strip():
        return {
            "language": "Unknown",
            "confidence": 0,
            "source": "none",
            "translation": "N/A",
            "word_level": [],
            "complexity": "N/A",
            "readability_score": 0,
            "complexity_note": "N/A",
            "sentence_type": "Unknown"
        }

    # 1. Pre-check: No alphabetic characters
    if not any(char.isalpha() for char in text):
        return {
            "language": "Unknown",
            "confidence": 0,
            "source": "pre_check",
            "translation": "N/A",
            "word_level": [],
            "complexity": "N/A",
            "readability_score": 0,
            "complexity_note": "N/A",
            "sentence_type": detect_sentence_type(text)
        }

    # 2. Gibberish heuristic check
    if is_gibberish(text):
        return {
            "language": "Unknown",
            "confidence": 0,
            "source": "gibberish_check",
            "translation": "N/A",
            "word_level": [],
            "complexity": "N/A",
            "readability_score": 0,
            "complexity_note": "N/A",
            "sentence_type": detect_sentence_type(text)
        }

    # 3. Main Logic
    lang, conf = predict_sentence(text)
    source = "ml_model"
    
    # 4. Fallback if confidence < 0.7
    if conf < 0.7:
        lang_ext, conf_ext = detect_external(text)
        if conf_ext > 0:
            lang, conf, source = lang_ext, conf_ext, "external"
        
    # 5. Smart 'Unknown' Threshold (User requested: confidence < 0.6 or words < 2)
    # Refined: confidence < 0.6 always Unknown, words < 2 requires higher confidence
    word_count = len(text.split())
    if conf < 0.6 or (word_count < 2 and conf < 0.9):
        lang = "Unknown"
        
    word_results = predict_word_level(text)
    translation = translate_to_english(text, lang) if lang != "Unknown" else "N/A"
    
    # 🔥 NEW FEATURE: Complexity Analysis
    score, complexity = analyze_complexity(text)
    complexity_note = "Accurate" if lang == "English" else "Best suited for English text"
    
    # 🔥 NEW FEATURE: Sentence Type
    sentence_type = detect_sentence_type(text)
    
    return {
        "language": lang,
        "confidence": conf,
        "source": source,
        "translation": translation,
        "word_level": word_results,
        "complexity": complexity,
        "readability_score": score,
        "complexity_note": complexity_note,
        "sentence_type": sentence_type
    }

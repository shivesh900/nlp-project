from langdetect import detect_langs, DetectorFactory

# Set seed for consistent results
DetectorFactory.seed = 0

class LanguageDetector:
    def __init__(self):
        # We can add more complex model initialization here if needed
        pass

    def predict(self, text: str):
        """
        Detects the language of the given text and returns the top prediction.
        """
        if not text or not text.strip():
            return {"language": "unknown", "confidence": 0.0}

        try:
            # detect_langs returns a list of Language objects with 'lang' and 'prob' attributes
            predictions = detect_langs(text)
            if predictions:
                top_prediction = predictions[0]
                return {
                    "language": top_prediction.lang,
                    "confidence": round(top_prediction.prob, 4)
                }
        except Exception as e:
            # Handle cases where detection fails (e.g., no features in text)
            print(f"Detection error: {e}")
            
        return {"language": "unknown", "confidence": 0.0}

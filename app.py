import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.predict import get_full_prediction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# IMPORTANT: Explicitly allow CORS for frontend integration
CORS(app, resources={r"/predict": {"origins": "*"}})

@app.route('/health', methods=['GET'])
def health_check():
    """
    Standard health check for deployment.
    """
    return jsonify({
        "status": "healthy", 
        "service": "Language-Detection-Backend",
        "version": "1.1.0"
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.
    Expects: JSON { "text": "..." }
    """
    try:
        # 1. Parse Input
        data = request.get_json(silent=True)
        if not data or 'text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'text' field in request body."
            }), 400
        
        text = str(data.get('text', '')).strip()
        if not text:
            return jsonify({
                "status": "error",
                "message": "Text input cannot be empty."
            }), 400
        
        # 2. Get Analysis
        result = get_full_prediction(text)
        
        # 3. Log Log Activity (Shortened)
        logger.info(f"Analyzed {len(text)} chars | Result: {result['language']} ({result['confidence']})")
        
        return jsonify(result), 200

    except Exception as e:
        logger.exception("Unexpected error during /predict execution")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred. Please check logs."
        }), 500

if __name__ == '__main__':
    # Using 0.0.0.0 for easier containerization/deployment
    logger.info("Starting Language Detection Backend on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)

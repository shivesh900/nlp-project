# Language Detection NLP Backend

A Flask-based backend for high-performance language detection using the `langdetect` library.

## Project Structure
```text
├── app.py             # Main Flask application
├── model/             # NLP Prediction logic
│   ├── __init__.py
│   └── detector.py    # LanguageDetector class
├── utils/             # Helper functions
│   ├── __init__.py
│   └── response_handler.py
└── requirements.txt   # Project dependencies
```

## Setup Instructions

### 1. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

## API Documentation

### Predict Language
- **URL**: `/predict`
- **Method**: `POST`
- **Body**:
  ```json
  {
      "text": "Hello, how are you?"
  }
  ```
- **Response**:
  ```json
  {
      "language": "en",
      "confidence": 0.9999
  }
  ```

### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**:
  ```json
  {
      "status": "success",
      "data": {
          "status": "healthy"
      }
  }
  ```

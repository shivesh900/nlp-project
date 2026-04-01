# Language Intelligence & Detection System

A multi-interface NLP system featuring a high-performance Flask API and a premium Streamlit dashboard for real-time language detection, translation, and text analysis.

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
---

## 🎨 Interactive Dashboard (Streamlit)

A premium user interface for analyzing text patterns, complexity, and word-level language distribution.

### Features
- **Real-time Prediction**: Hybrid ML + fallback detection.
- **Complexity Analysis**: Flesch Reading Ease scores.
- **Word-Level Breakdown**: Highlighted language detection for individual words.
- **Automated Translation**: Instant translation to English.

### Local Run
```bash
streamlit run streamlit_app.py
```

### Streamlit Community Cloud
Visit the live dashboard (if deployed) or follow the [Deployment Guide](DEPLOYMENT.md) to set it up on Streamlit Cloud.

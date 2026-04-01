# Deployment Guide

This guide provides step-by-step instructions for deploying the Language Detection NLP System.

## 🚀 Backend Deployment (Render / Railway)

### 1. Prepare Backend Files
Ensure your root directory has these files:
- `app.py`
- `requirements.txt`
- `model.pkl`
- `vectorizer.pkl`
- `utils/`
- `runtime.txt` (Optional, specifies Python version)
- `Procfile` (For Render/Heroku)

### 2. Create `Procfile`
Create a file named `Procfile` in the root directory:
```text
web: gunicorn app:app
```

### 3. Create `runtime.txt`
Create a file named `runtime.txt` in the root directory:
```text
python-3.10.12
```

### 4. Deploy on Render
1. Create a new **Web Service** on Render.
2. Connect your GitHub repository.
3. **Runtime**: Python.
4. **Build Command**: `pip install -r requirements.txt`.
5. **Start Command**: `gunicorn app:app`.
6. **Environment Variables**:
   - `PORT`: `5000` (Optional, Render assigns one automatically).

---

## 🎨 Frontend Deployment (Vercel)

### 1. Update API URL
In your frontend, ensure the API URL points to your deployed backend. You can use an environment variable:
- Create a `.env.production` file in `frontend/`:
  ```text
  VITE_API_URL=https://your-backend-url.onrender.com/predict
  ```

### 2. Deploy on Vercel
1. Run `npm run build` locally to verify (optional).
2. Go to [Vercel](https://vercel.com) and import your project.
3. Select the `frontend` directory as the **Root Directory**.
4. **Framework Preset**: Vite.
5. **Build Command**: `npm run build`.
6. **Output Directory**: `dist`.
7. **Environment Variables**:
   - `VITE_API_URL`: Your deployed backend URL + `/predict`.

### 3. Deployment Configuration (`vercel.json`)
If you need routing for Single Page Application (SPA), create `frontend/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## 🌩️ Streamlit Community Cloud Deployment (Easiest)

This method is recommended for the **NLP Language Intelligence dashboard** (`streamlit_app.py`).

### 1. Prerequisites
- **GitHub Repository**: Your code MUST be pushed to a public or private GitHub repository.
- **`requirements.txt`**: Ensure this file is in the root and contains `streamlit`, `scikit-learn`, `googletrans==4.0.0-rc1`, etc.
- **Model Files**: `model.pkl` and `vectorizer.pkl` must be in the root directory.

### 2. Deployment Steps
1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **New app** -> **Use existing repo**.
4. Select your repository and branch.
5. Set the **Main file path** to `streamlit_app.py`.
6. Click **Deploy!**

### 3. Troubleshooting
- **Model not loading**: Ensure `model.pkl` is committed and pushed. Streamlit Cloud has a 1GB limit, but our models are <1MB.
- **Translation Errors**: `googletrans` can be unstable. If translation fails, check the logs in the Streamlit Cloud dashboard.

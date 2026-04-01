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

## ✅ Post-Deployment Verification
- Test the frontend URL.
- Enter text in English, Tamil, or Hindi.
- Verify that the detection highlight and translation appear correctly.

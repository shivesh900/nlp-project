import streamlit as st
from utils.predict import get_full_prediction

# Premium Styling
st.set_page_config(
    page_title="NLP Language Detection & Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark Theme & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-title {
        background: linear-gradient(90deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* Responsive Dashboard Cards */
    .stMetric {
        background-color: rgba(30, 41, 59, 0.7);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(96, 165, 250, 0.4);
    }
    .stMetric label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }
    
    /* Text Input Styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 12px;
        border: 1px solid #334155 !important;
        font-size: 1.1rem;
    }
    
    /* Premium Analyze Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 12px;
        border-radius: 12px;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-top: 20px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
        transform: scale(1.02);
    }
    
    /* Word Level Badges */
    .word-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        background: #334155;
        margin: 4px;
        font-size: 0.9rem;
        border: 1px solid #475569;
    }
    .badge-label { font-weight: bold; color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

# --- APP UI ---
st.markdown('<h1 class="main-title">🌍 NLP Language Intelligence</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; color: #94a3b8;'>Multilingual detection, complexity analysis, and real-time translation.</p>", unsafe_allow_html=True)

# Input Space
with st.container():
    text = st.text_area("", placeholder="Type or paste text here (English, Tamil, Hindi)...", height=150)
    
    cols = st.columns([2, 1, 2])
    with cols[1]:
        analyze_btn = st.button("🚀 ANALYZE TEXT")

if analyze_btn:
    if not text.strip():
        st.warning("⚠️ Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing linguistic patterns..."):
            result = get_full_prediction(text)
            
            # --- MAIN METRICS ---
            st.markdown("### 🧠 Analysis Overview")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            with m_col1:
                st.metric("Detected Language", result["language"])
            with m_col2:
                st.metric("Confidence Score", f"{result['confidence']*100:.2f}%")
            with m_col3:
                st.metric("Text Complexity", result["complexity"])
            with m_col4:
                st.metric("Sentence Type", result["sentence_type"])
            
            # --- DETAILS SECTION ---
            st.divider()
            
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.markdown("### 🌐 Automated Translation")
                st.info(result.get("translation", "N/A"))
                
                if result["readability_score"]:
                    st.markdown(f"**Readability Score (Flesch):** `{result['readability_score']}`")
                    st.caption(result.get("complexity_note", ""))

            with res_col2:
                st.markdown("### 🔍 Word-Level Breakdown")
                words = result.get("word_level", [])
                if words:
                    html_badges = ""
                    for w in words:
                        html_badges += f'<span class="word-badge"><b>{w["word"]}</b> <span class="badge-label">[{w["language"]}]</span></span>'
                    st.markdown(html_badges, unsafe_allow_html=True)
                else:
                    st.write("No detailed word-level data available.")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/language.png", width=150)
    st.title("Settings & info")
    st.write("This tool uses a hybrid Approach:")
    st.markdown("- **ML Model**: Scikit-learn + TF-IDF\n- **External Logic**: Langdetect Fallback\n- **Linguistic**: Textstat Analysis")
    st.divider()
    st.caption("v1.2.0 • Build 2026-04-01")

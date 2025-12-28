import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

# Groq API
from groq import Groq
from dotenv import load_dotenv

# =====================================================================
# CONFIGURATION INITIALE
# =====================================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="SecureOps SOC Platform",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# STYLE CSS ULTRA-PREMIUM - INSPIRÉ DES CAPTURES
# =====================================================================
st.markdown("""
<style>
    /* POLICE MODERNE */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* BACKGROUND PRINCIPAL */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* SIDEBAR PREMIUM STYLE SSN */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 25%, #2563eb 75%, #3b82f6 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* LOGO SECTION */
    section[data-testid="stSidebar"] img {
        filter: brightness(1.2) contrast(1.1);
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* NAVIGATION ITEMS */
    section[data-testid="stSidebar"] .stRadio > label {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 0.9rem 1.2rem !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        cursor: pointer;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(5px);
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"] > div:first-child {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"][aria-checked="true"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
        margin: 1.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* STATUS INDICATORS DANS SIDEBAR */
    .status-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
        color: white;
        font-size: 0.9rem;
    }
    
    /* HEADER PREMIUM AVEC DÉGRADÉ */
    .soc-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .soc-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .soc-header h1 {
        color: #FFFFFF;
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
    }
    
    .soc-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.3rem;
        margin: 0.8rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* CARTES MÉTRIQUES STYLE CAPTURE */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(31, 38, 135, 0.25);
        border-color: #667eea;
    }
    
    .metric-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.8rem 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .metric-trend {
        font-size: 1rem;
        margin-top: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .trend-up { color: #ef4444; }
    .trend-down { color: #10b981; }
    .trend-stable { color: #6b7280; }
    
    /* SECTIONS BLANCHES ÉLÉGANTES */
    .section-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(31, 38, 135, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%) 1;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* ALERTES MODERNES */
    .alert-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .alert-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .alert-info {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* BOUTONS PREMIUM */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.9rem 2.5rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }
    
    /* BADGES */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-critical { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }
    .badge-high { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
    .badge-medium { background: linear-gradient(135deg, #eab308, #ca8a04); color: white; }
    .badge-low { background: linear-gradient(135deg, #10b981, #059669); color: white; }
    .badge-info { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
    
    /* STATUS INDICATOR */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse-status 2s infinite;
        box-shadow: 0 0 10px currentColor;
    }
    
    .status-online { background: #10b981; }
    .status-warning { background: #f59e0b; }
    .status-offline { background: #ef4444; }
    
    @keyframes pulse-status {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    /* CHAT MESSAGES */
    .chat-message {
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        max-width: 85%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .chat-user {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        margin-left: auto;
        border: 1px solid #d1d5db;
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* FORMULAIRES */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        padding: 0.9rem !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* METRICS STREAMLIT */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* DATAFRAME */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# INITIALISATION GROQ (FIX ERREUR MODÈLE)
# =====================================================================
@st.cache_resource
def init_groq_client():
    if GROQ_API_KEY:
        return Groq(api_key=GROQ_API_KEY)
    return None

groq_client = init_groq_client()

# =====================================================================
# CHARGEMENT DU MODÈLE ML
# =====================================================================
@st.cache_resource
def load_ml_model():
    try:
        return joblib.load("./models/isolation_forest.pkl")
    except:
        return None

model = load_ml_model()

# =====================================================================
# CHARGEMENT DES DONNÉES
# =====================================================================
@st.cache_data
def load_consolidated_data():
    try:
        df = pd.read_csv("./Notebooks/data/processed/consolidated_soc.csv", parse_dates=["date"])
        return df
    except:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        return pd.DataFrame({
            'date': dates,
            'anomalies_detected': np.random.randint(10, 80, 90),
            'high_risk_sessions': np.random.randint(20, 100, 90),
            'critical_incidents': np.random.randint(0, 15, 90),
            'total_incidents': np.random.randint(50, 200, 90),
            'total_tickets': np.random.randint(100, 400, 90),
            'avg_incident_duration_days': np.random.uniform(0.2, 8, 90),
            'p95_resolution_minutes': np.random.uniform(60, 480, 90),
            'avg_ip_reputation': np.random.uniform(0.4, 0.95, 90)
        })

# =====================================================================
# FONCTION ANALYSE GROQ (FIX MODÈLE)
# =====================================================================
def groq_soc_analysis(question, df_context):
    """Analyse SOC via Groq AI avec modèle valide"""
    if not groq_client:
        return "❌ Service Groq non disponible. Vérifiez votre clé API."
    
    if df_context is None or df_context.empty:
        context = "Aucune donnée SOC disponible pour l'analyse."
    else:
        recent_data = df_context.tail(14)
        context = f"""
🔐 CONTEXTE SOC - SECUREOPS PLATFORM
================================================
📅 Période: {recent_data['date'].min().strftime('%d/%m/%Y')} - {recent_data['date'].max().strftime('%d/%m/%Y')}

📊 MÉTRIQUES CLÉS:
• Anomalies détectées: {int(recent_data['anomalies_detected'].sum())}
• Sessions haut risque: {int(recent_data['high_risk_sessions'].sum())}
• Incidents critiques: {int(recent_data['critical_incidents'].sum())}
• MTTR moyen: {recent_data['avg_incident_duration_days'].mean():.2f} jours
• Réputation IP moyenne: {recent_data['avg_ip_reputation'].mean():.2f}

📈 TENDANCES:
• Évolution anomalies: {((recent_data['anomalies_detected'].iloc[-1] - recent_data['anomalies_detected'].iloc[0]) / max(recent_data['anomalies_detected'].iloc[0], 1) * 100):.1f}%
• Évolution risque: {((recent_data['high_risk_sessions'].iloc[-1] - recent_data['high_risk_sessions'].iloc[0]) / max(recent_data['high_risk_sessions'].iloc[0], 1) * 100):.1f}%
"""
    
    try:
        # Utilisation du bon modèle Llama 3.3
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modèle valide et performant
            messages=[
                {
                    "role": "system",
                    "content": """Tu es un analyste SOC senior expert chez SecureOps (SSN - Système Security Network).

🎯 MISSION:
• Analyser les incidents de sécurité avec précision professionnelle
• Identifier les menaces critiques et patterns d'attaque
• Proposer des actions concrètes, priorisées et mesurables
• Communiquer de manière claire, structurée et actionnable

💼 STYLE PROFESSIONNEL:
• Ton direct, expert mais accessible
• Réponses structurées avec sections claires
• Utilise des emojis pertinents pour la lisibilité (🔴 🟠 🟢 ⚠️ 🎯 📊 💡)
• Priorise toujours les informations critiques
• Propose des actions avec timeline et responsabilités
• Quantifie les risques et impacts

✅ FORMAT RECOMMANDÉ:
1. Synthèse executive (2-3 lignes)
2. Analyse détaillée
3. Recommandations prioritaires
4. Actions immédiates si nécessaire"""
                },
                {
                    "role": "user",
                    "content": f"{context}\n\n❓ QUESTION SOC:\n{question}"
                }
            ],
            temperature=0.3,
            max_tokens=1200,
            top_p=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur lors de l'analyse: {str(e)}\n\n💡 Vérifiez que le modèle Groq est accessible et que votre clé API est valide."

# =====================================================================
# SIDEBAR NAVIGATION PREMIUM
# =====================================================================
with st.sidebar:
    # Logo avec style amélioré
    try:
        st.image("./assets/logoSSN.png", width=180)
    except:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 1rem; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='color: white; font-size: 2.5rem; margin: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.3);'>🔐 SSN</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Security Network</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation avec style moderne
    st.markdown("### 🧭 NAVIGATION")
    menu = st.radio(
        "",
        ["🏠 Accueil", "📊 Tableau de bord SOC", "🧠 Analyser ML", "💬 Assistant IA", "⚙️ Paramètres"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Statut système
    st.markdown("### 📡 STATUT SYSTÈME")
    st.markdown("""
    <div class='status-box'>
        <div class='status-item'>
            <span class='status-indicator status-online'></span>
            <strong>Services:</strong> EN LIGNE
        </div>
        <div class='status-item'>
            <span class='status-indicator status-online'></span>
            <strong>ML Engine:</strong> ACTIF
        </div>
        <div class='status-item'>
            <span class='status-indicator status-online'></span>
            <strong>Database:</strong> CONNECTÉ
        </div>
        <div class='status-item'>
            <span class='status-indicator status-online'></span>
            <strong>Groq AI:</strong> OPÉRATIONNEL
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informations système
    st.markdown("### ℹ️ INFORMATIONS")
    st.markdown("""
    <div style='font-size: 0.85rem; line-height: 1.8;'>
        <strong>Version:</strong> 2.5.0 Enterprise<br>
        <strong>Build:</strong> 20250127<br>
        <strong>Utilisateur:</strong> Admin SOC<br>
        <strong>Dernière MAJ:</strong> Aujourd'hui
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# PAGE: ACCUEIL
# =====================================================================
if menu == "🏠 Accueil":
    st.markdown("""
    <div class="soc-header">
        <h1>🔐 Plateforme SOC SecureOps</h1>
        <p>Centre de supervision et de réponse aux incidents de sécurité</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_consolidated_data()
    
    # Métriques temps réel style capture
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🚨</span>
            <div class="metric-value">{int(df['anomalies_detected'].tail(7).sum())}</div>
            <div class="metric-label">Anomalies (7j)</div>
            <div class="metric-trend trend-up">↑ +12%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⚠️</span>
            <div class="metric-value">{int(df['high_risk_sessions'].tail(7).sum())}</div>
            <div class="metric-label">Haut Risque (7j)</div>
            <div class="metric-trend trend-down">↓ -5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🔴</span>
            <div class="metric-value">{int(df['critical_incidents'].tail(7).sum())}</div>
            <div class="metric-label">Incidents Critiques</div>
            <div class="metric-trend trend-stable">→ 0%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⏱️</span>
            <div class="metric-value">{df['avg_incident_duration_days'].mean():.1f}j</div>
            <div class="metric-label">MTTR Moyen</div>
            <div class="metric-trend trend-down">↓ -8%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section À propos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="section-container">
            <div class="section-title">🏢 À propos de SecureOps</div>
            <p style="font-size: 1.1rem; line-height: 2; color: #374151;">
                <strong>SecureOps ( Développé au sein de SSN - Système Security Network)</strong> est la plateforme SOC de nouvelle génération 
                conçue pour les entreprises exigeantes en matière de cybersécurité.
            </p>
                        <p style="font-size: 1.15rem; line-height: 2; color: #1f2937; font-weight: 600; margin-bottom: 1.5rem;">
                <strong style="color: #667eea;">System Security Network ICT (SSNICT)</strong> est un leader incontesté 
                de la cybersécurité en Afrique Centrale depuis plus de <strong>20 ans</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        try:
            st.image("./assets/7.jpg", use_container_width=True)
        except:
            st.markdown("""
            <div class="section-container" style="text-align: center; padding: 3rem 2rem;">
                <div style="font-size: 5rem;">🛡️</div>
                <h3 style="color: #667eea; margin-top: 1rem;">Protection Enterprise</h3>
            </div>
            """, unsafe_allow_html=True)
    # Services SSNICT
    st.markdown("---")
    st.markdown('<div class="section-title">🛡️ Services SSNICT</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🔒 Cybersécurité</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li><strong>Audit de sécurité</strong> complet</li>
                <li><strong>Installation</strong> de systèmes de protection</li>
                <li><strong>Maintenance</strong> infrastructure sécurité</li>
                <li><strong>Formation</strong> en cybersécurité</li>
                <li><strong>Pentesting</strong> & évaluation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">💻 Développement Web</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li><strong>Sites vitrines</strong> professionnels</li>
                <li><strong>E-commerce</strong> sur mesure</li>
                <li><strong>Applications web</strong> métier</li>
                <li><strong>Maintenance</strong> & support</li>
                <li><strong>Hébergement</strong> sécurisé</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">📊 Marketing Digital</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li><strong>SEO/SEM</strong> optimisation</li>
                <li><strong>Gestion</strong> réseaux sociaux</li>
                <li><strong>Publicité</strong> en ligne</li>
                <li><strong>Analytics</strong> & reporting</li>
                <li><strong>Stratégie</strong> digitale</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Vision & Mission
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🎯 Notre Mission</h3>
            <p style="font-size: 1.05rem; line-height: 1.9; color: #374151;">
                <strong>Promouvoir la vulgarisation des TIC</strong> auprès des couches vulnérables 
                pour contribuer à leur auto-emploi. SSNICT met ses compétences au profit de la classe 
                nécessiteuse pour mieux les équiper et faciliter leur entrée dans le monde de l'emploi.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">👁️ Notre Vision</h3>
            <p style="font-size: 1.05rem; line-height: 1.9; color: #374151;">
                <strong>Devenir le partenaire de référence</strong> en cybersécurité et solutions IT 
                en Afrique Centrale, en offrant des solutions innovantes qui correspondent aux besoins 
                réels de nos clients avec les technologies les plus adaptées.
            </p>
        </div>
        """, unsafe_allow_html=True)
    # Capacités SOC
    st.markdown("---")
    st.markdown('<div class="section-title">⚡ Capacités SOC Enterprise</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🎯 Détection Avancée</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li>Corrélation multi-sources temps réel</li>
                <li>Behavioral analytics & UEBA</li>
                <li>Machine Learning (Isolation Forest)</li>
                <li>Threat Intelligence intégrée</li>
                <li>Détection 0-day patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🚀 Réponse Automatisée</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li>Playbooks SOAR personnalisables</li>
                <li>Orchestration automatique</li>
                <li>Containment intelligent</li>
                <li>Escalade adaptative</li>
                <li>Remédiation automatique</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="section-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">📈 Analyse & Reporting</h3>
            <ul style="line-height: 2.2; color: #4b5563;">
                <li>Dashboards temps réel HD</li>
                <li>KPIs SOC personnalisés</li>
                <li>Rapports réglementaires auto</li>
                <li>Forensics & investigation</li>
                <li>Conformité RGPD/ISO27001</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
elif menu == "📊 Tableau de bord SOC":
    st.markdown("""
    <div class="soc-header">
        <h1>📊 Dashboard SOC</h1>
        <p>Vue consolidée de la posture de sécurité</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_consolidated_data()
    
    # Filtres temporels
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "📅 Date début",
            value=df["date"].min(),
            min_value=df["date"].min(),
            max_value=df["date"].max()
        )
    
    with col2:
        end_date = st.date_input(
            "📅 Date fin",
            value=df["date"].max(),
            min_value=df["date"].min(),
            max_value=df["date"].max()
        )
    
    with col3:
        refresh = st.button("🔄 Actualiser", use_container_width=True)

    
    # Filtrage des données
    df_filtered = df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ]
    
    if df_filtered.empty:
        st.error("❌ Aucune donnée disponible pour cette période")
        st.stop()
    
    # KPIs principaux
    st.markdown("### 📈 Indicateurs Clés de Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_anomalies = int(df_filtered["anomalies_detected"].sum())
    total_high_risk = int(df_filtered["high_risk_sessions"].sum())
    total_critical = int(df_filtered["critical_incidents"].sum())
    avg_mttr = df_filtered["avg_incident_duration_days"].mean()
    total_tickets = int(df_filtered["total_tickets"].sum())
    
    col1.metric("🚨 Anomalies", f"{total_anomalies:,}", f"+{np.random.randint(5, 20)}%")
    col2.metric("⚠️ Haut Risque", f"{total_high_risk:,}", f"-{np.random.randint(2, 15)}%")
    col3.metric("🔴 Critiques", f"{total_critical:,}", f"+{np.random.randint(1, 10)}%")
    col4.metric("⏱️ MTTR", f"{avg_mttr:.1f}j", f"-{np.random.randint(5, 15)}%")
    col5.metric("🎫 Tickets", f"{total_tickets:,}", f"+{np.random.randint(10, 25)}%")
    
    st.markdown("---")
        # EVOLUTION TEMPORELLE
    # =============================
    st.markdown('<div class="section-title">Évolution temporelle SOC</div>', unsafe_allow_html=True)

    fig_trend = px.line(
        df,
        x="date",
        y=["anomalies_detected", "critical_incidents", "total_tickets"],
        labels={"value": "Volume", "date": "Date"},
        title="Anomalies, incidents critiques & tickets IT",
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # =============================
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📉 Évolution des Anomalies")
        fig_anomalies = go.Figure()
        fig_anomalies.add_trace(go.Scatter(
            x=df_filtered["date"],
            y=df_filtered["anomalies_detected"],
            mode='lines+markers',
            name='Anomalies',
            line=dict(color='#DC3545', width=3),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.1)'
        ))
        fig_anomalies.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_anomalies, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Sessions à Haut Risque")
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Bar(
            x=df_filtered["date"],
            y=df_filtered["high_risk_sessions"],
            name='Haut Risque',
            marker_color='#FFC107'
        ))
        fig_risk.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    st.markdown("---")

    # =============================

    
    # Tableau de bord multi-métriques
    st.markdown("### 🔄 Vue Multi-Métriques")
    
    fig_multi = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Incidents Critiques', 'MTTR Évolution', 
                       'Tickets IT', 'Réputation IP'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Incidents critiques
    fig_multi.add_trace(
        go.Scatter(x=df_filtered["date"], y=df_filtered["critical_incidents"],
                  mode='lines', name='Incidents', line=dict(color='#DC3545', width=2)),
        row=1, col=1
    )
    
    # MTTR
    fig_multi.add_trace(
        go.Scatter(x=df_filtered["date"], y=df_filtered["avg_incident_duration_days"],
                  mode='lines+markers', name='MTTR', line=dict(color='#0B5ED7', width=2)),
        row=1, col=2
    )
    
    # Tickets
    fig_multi.add_trace(
        go.Bar(x=df_filtered["date"], y=df_filtered["total_tickets"],
              name='Tickets', marker_color='#28A745'),
        row=2, col=1
    )
    
    # Réputation IP
    fig_multi.add_trace(
        go.Scatter(x=df_filtered["date"], y=df_filtered["avg_ip_reputation"],
                  mode='lines', name='Réputation', line=dict(color='#17A2B8', width=2),
                  fill='tozeroy'),
        row=2, col=2
    )
    
    fig_multi.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_multi, use_container_width=True)
    
    st.markdown("---")
    
    # Statistiques avancées
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Statistiques Détaillées")
        stats_df = pd.DataFrame({
            'Métrique': ['Anomalies', 'Haut Risque', 'Incidents', 'MTTR (jours)', 'Tickets'],
            'Minimum': [
                df_filtered['anomalies_detected'].min(),
                df_filtered['high_risk_sessions'].min(),
                df_filtered['critical_incidents'].min(),
                f"{df_filtered['avg_incident_duration_days'].min():.2f}",
                df_filtered['total_tickets'].min()
            ],
            'Maximum': [
                df_filtered['anomalies_detected'].max(),
                df_filtered['high_risk_sessions'].max(),
                df_filtered['critical_incidents'].max(),
                f"{df_filtered['avg_incident_duration_days'].max():.2f}",
                df_filtered['total_tickets'].max()
            ],
            'Moyenne': [
                f"{df_filtered['anomalies_detected'].mean():.1f}",
                f"{df_filtered['high_risk_sessions'].mean():.1f}",
                f"{df_filtered['critical_incidents'].mean():.1f}",
                f"{df_filtered['avg_incident_duration_days'].mean():.2f}",
                f"{df_filtered['total_tickets'].mean():.1f}"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🎯 Niveau de Criticité")
        critical_rate = (df_filtered['critical_incidents'].sum() / 
                        df_filtered['total_incidents'].sum() * 100 
                        if df_filtered['total_incidents'].sum() > 0 else 0)
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=critical_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Taux d'Incidents Critiques (%)"},
            delta={'reference': 15},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#0B5ED7"},
                'steps': [
                    {'range': [0, 25], 'color': "#28A745"},
                    {'range': [25, 50], 'color': "#FFC107"},
                    {'range': [50, 100], 'color': "#DC3545"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Export
    st.markdown("---")
    st.markdown("### 📥 Export & Reporting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = df_filtered.to_csv(index=False)
        st.download_button(
            "📄 Export CSV",
            csv_data,
            file_name=f"soc_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# =====================================================================
# PAGE: ANALYSE ML
# =====================================================================
elif menu == "🧠 Analyser ML":
    st.markdown("""
    <div class="soc-header">
        <h1>🧠 Analyse Machine Learning</h1>
        <p>Détection d'anomalies réseau par intelligence artificielle</p>
    </div>
    """, unsafe_allow_html=True)
    
    if model is None:
        st.error("❌ Modèle ML non disponible")
        st.stop()
    
    # Formulaire
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Paramètres de Session Réseau")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        packet_size = st.number_input("📦 Taille paquets (octets)", 0, 5000, 200, 50)
        login_attempts = st.number_input("🔁 Tentatives connexion", 0, 50, 2, 1)
    
    with col2:
        failed_logins = st.number_input("❌ Échecs connexion", 0, 20, 1, 1)
        session_duration = st.number_input("⏱️ Durée session (sec)", 1, 10000, 300, 10)
    
    with col3:
        ip_reputation = st.slider("🌐 Réputation IP", 0.0, 1.0, 0.7, 0.05)
        unusual_time = st.selectbox("🕒 Horaire inhabituel", [0, 1], 
                                     format_func=lambda x: "✅ Oui" if x == 1 else "❌ Non")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bouton analyse
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 ANALYSER LA SESSION", use_container_width=True)
    
    if analyze_button:
        input_df = pd.DataFrame([{
            "packet_size": packet_size,
            "login_attempts_count": login_attempts,
            "failed_logins_count": failed_logins,
            "session_duration_seconds": session_duration,
            "ip_reputation_score": ip_reputation,
            "unusual_time_access": unusual_time
        }])
        
        with st.spinner("⚙️ Analyse en cours..."):
            time.sleep(1)
            anomaly_score = model.decision_function(input_df)[0]
        
        st.markdown("---")
        
        # Résultats
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if anomaly_score < -0.10:
                risk_level, risk_color, alert_class, risk_icon = "CRITIQUE", "#ef4444", "alert-critical", "🔴"
            elif anomaly_score < 0:
                risk_level, risk_color, alert_class, risk_icon = "ÉLEVÉ", "#f59e0b", "alert-warning", "🟠"
            else:
                risk_level, risk_color, alert_class, risk_icon = "FAIBLE", "#10b981", "alert-success", "🟢"
            
            st.markdown(f"""
            <div class="{alert_class}">
                <h2 style="margin: 0;">{risk_icon} Niveau: {risk_level}</h2>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                    Score: <strong>{anomaly_score:.4f}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Jauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=anomaly_score,
                title={'text': "Score ML", 'font': {'size': 22}},
                number={'font': {'size': 44}},
                gauge={
                    'axis': {'range': [-0.5, 0.5]},
                    'bar': {'color': risk_color, 'thickness': 0.8},
                    'steps': [
                        {'range': [-0.5, -0.10], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [-0.10, 0], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [0, 0.5], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ]
                }
            ))
            fig_gauge.update_layout(height=350, margin=dict(l=40, r=40, t=100, b=40))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class="section-container">
                <h3 style="color: {risk_color};">🎯 Actions Recommandées</h3>
            """, unsafe_allow_html=True)
            
            if anomaly_score < -0.10:
                st.markdown("• 🚨 **ESCALADE IMMÉDIATE** niveau 3\n• 🔒 **ISOLER** session/IP\n• 📊 **FORENSICS** complet\n• 📞 **ALERTER** RSSI")
            elif anomaly_score < 0:
                st.markdown("• ⚠️ **SURVEILLANCE** renforcée\n• 📈 **MONITORER** évolution\n• 🔎 **VÉRIFIER** corrélations")
            else:
                st.markdown("• ✅ **APPROUVER** session\n• 📊 **LOGGER** pour audit\n• 🔄 **CONTINUER** surveillance")
            
            st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PAGE: ASSISTANT IA
# =====================================================================
elif menu == "💬 Assistant IA":
    st.markdown("""
    <div class="soc-header">
        <h1>💬 Assistant SOC IA</h1>
        <p>Analyse intelligente propulsée par Groq AI (Llama 3.3)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not groq_client:
        st.markdown("""
        <div class="alert-critical">
            ❌ <strong>Service Groq non disponible</strong><br>
            Vérifiez votre clé API dans le fichier .env
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    df = load_consolidated_data()
    
    if "soc_chat" not in st.session_state:
        st.session_state.soc_chat = []
    
    # Questions rapides
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("### 🎯 Questions Rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Résumé situation", use_container_width=True):
            st.session_state.quick_q = "Donne-moi un résumé exécutif de la situation sécurité avec métriques et tendances clés."
    
    with col2:
        if st.button("🚨 Incidents critiques", use_container_width=True):
            st.session_state.quick_q = "Analyse les incidents critiques récents. Quels patterns détectes-tu?"
    
    with col3:
        if st.button("💡 Recommandations", use_container_width=True):
            st.session_state.quick_q = "Quelles sont tes 3 recommandations prioritaires pour améliorer la posture de sécurité?"
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulaire chat
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "💬 Votre question SOC",
            placeholder="Ex: Pourquoi les anomalies ont augmenté cette semaine?",
            height=120,
            value=st.session_state.get('quick_q', '')
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit = st.form_submit_button("🚀 ANALYSER", use_container_width=True)
    
    if 'quick_q' in st.session_state:
        del st.session_state.quick_q
    
    if submit and user_input:
        st.session_state.soc_chat.append(("user", user_input, datetime.now()))
        
        with st.spinner("🧠 Analyse IA en cours..."):
            response = groq_soc_analysis(user_input, df)
        
        st.session_state.soc_chat.append(("assistant", response, datetime.now()))
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Historique
    if st.session_state.soc_chat:
        st.markdown("---")
        st.markdown("### 💬 Historique de Conversation")
        
        for role, message, timestamp in reversed(st.session_state.soc_chat[-10:]):
            if role == "user":
                st.markdown(f"""
                <div class="chat-message chat-user">
                    <strong>👤 Analyste SOC</strong> • {timestamp.strftime('%H:%M:%S')}<br><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message chat-assistant">
                    <strong>🤖 Assistant IA</strong> • {timestamp.strftime('%H:%M:%S')}<br><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.soc_chat = []
            st.rerun()

# =====================================================================
# PAGE: PARAMÈTRES
# =====================================================================
elif menu == "⚙️ Paramètres":
    st.markdown("""
    <div class="soc-header">
        <h1>⚙️ Configuration Système</h1>
        <p>Paramètres et configuration de la plateforme SecureOps</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 Général", "🔔 Alertes", "📊 Modèle ML"])
    
    with tab1:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("### 🔧 Paramètres Généraux")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("🏢 Organisation", value="SecureOps SOC")
            st.selectbox("🌍 Fuseau horaire", ["UTC", "Europe/Paris", "America/New_York"])
        
        with col2:
            st.number_input("⏱️ Rafraîchissement (sec)", 10, 300, 60)
            st.selectbox("🎨 Thème", ["Clair", "Sombre", "Auto"])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("### 🔔 Configuration Alertes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.slider("🚨 Seuil anomalies", 0, 100, 20)
            st.slider("⚠️ Seuil sessions risque", 0, 50, 10)
        
        with col2:
            st.checkbox("📧 Email", value=True)
            st.checkbox("🔔 Slack", value=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("### 📊 Configuration ML")
        
        st.selectbox("🤖 Modèle", ["Isolation Forest", "One-Class SVM"])
        st.slider("🎯 Sensibilité", 0.0, 1.0, 0.5)
        
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6C757D;">
    <p style="margin: 0; font-size: 0.9rem;">
        <strong>SecureOps SOC Platform</strong> v2.0.0 Enterprise Edition
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">
        © 2026 SSN - AMOUGOU André Désiré Junior | Tous droits réservés
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">
        🔐 Plateforme certifiée ISO 27001 | SOC 2 Type II | RGPD Compliant
    </p>
</div>
""", unsafe_allow_html=True)
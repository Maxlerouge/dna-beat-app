import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import calendar

# --- DESIGN FUTURISTE ---
st.set_page_config(page_title="Agathe Budget", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 20px; }
    .stButton>button { width: 100%; border-radius: 25px; border: 1px solid #00f2fe; background: transparent; color: #00f2fe; transition: 0.3s; }
    .stButton>button:hover { background: #00f2fe; color: #000; box-shadow: 0 0 15px #00f2fe; }
    .discipline-score { font-size: 2.5rem; text-align: center; color: #00f2fe; font-weight: bold; text-shadow: 0 0 10px #00f2fe; }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION SÉCURISÉE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Historique", ttl=0)
        # Sécurité : Forcer les colonnes si le sheet est vide
        cols = ["Date", "Nom", "Montant", "Type", "Mode"]
        if df is None or df.empty:
            return pd.DataFrame(columns=cols)
        for col in cols:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

# --- INITIALISATION MÉMOIRE (SESSION) ---
if 'solde_reporte' not in st.session_state: st.session_state.solde_reporte = 0.0
if 'tresor_agathe' not in st.session_state: st.session_state.tresor_agathe = 0.0

# --- SIDEBAR : TOUTES TES VARIABLES ---
with st.sidebar:
    st.title("🛸 NAVIGATION")
    mode_urgence = st.toggle("🚨 MODE URGENCE", value=False)
    
    with st.expander("💰 REVENUS (Instituteur d'État)", expanded=False):
        sal = st.number_input("Salaire base (€)", value=3500)
        irl = st.number_input("Indemnité IRL (€)", value=300)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer perçu (€)", value=588)
        h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    with st.expander("🏠 CHARGES FIXES", expanded=False):
        loyer_out = st.number_input("Loyer emprunt (€)", value=850)
        assu_emp = st.number_input("Assurance emprunt (€)", value=200)
        tel_net = st.number_input("Tel + Internet (€)", value=90)
        edf_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        voiture = st.number_input("Kona + Assu (€)", value=415)
        famille = st.number_input("Enfants (€)", value=200)
        divers = st.number_input("Autres (€)", value=110)

    with st.expander("🎯 STRATÉGIE", expanded=True):
        remboursement = st.number_input("Remboursement Découvert (€)", value=600)
        courses_max = st.slider("Budget Courses (€)", 300, 900, 600)
        active_agathe = st.toggle("Épargne Agathe (1000€)", value=False)

# --- CALCULS ---
now = datetime.now()
jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
total_rev = sal + irl + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_agathe = 1000 if active_agathe else 0
courses_prevues = courses_max * 0.7 if mode_urgence else courses_max

reste_mensuel = total_rev - total_charges - courses_prevues - remboursement - epargne_agathe
budget_jour_base = reste_mensuel / jours_dans_le_mois

# --- INTERFACE ---
st.title("🧬 Agathe Budget : Forteresse")

tab1, tab2, tab3 = st.tabs(["⚡ PILOTAGE", "📑 HISTORIQUE", "💎 TRÉSOR"])

with tab1:
    df_h = load_data()
    aujourdhui = now.strftime("%Y-%m-%d")
    
    # Calcul sécurisé
    try:
        depenses_today = pd.to_numeric(df_h[df_h["Date"] == aujourdhui]["Montant"], errors='coerce').sum()
    except:
        depenses_today = 0.0
        
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    # Score Discipline
    try:
        total_depense_mois = pd.to_numeric(df_h["Montant"], errors='coerce').sum()
        score = max(0, min(100, int(100 - (total_depense_mois / (reste_mensuel + 1) * 100))))
    except:
        score = 100

    # RÉPARATION ICI : Ajout des parenthèses ()
    col1, col2, col3 = st.columns(3)
    col1.metric("OBJECTIF JOUR", f"{budget_jour_base:.2f} €")
    col2.metric("RESTE

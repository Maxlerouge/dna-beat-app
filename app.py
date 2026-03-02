import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import calendar

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Agathe Budget", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 15px; padding: 20px; }
    .stButton>button { width: 100%; border-radius: 25px; border: 1px solid #00f2fe; background: transparent; color: #00f2fe; }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION DIRECTE VIA URL ---
def connect_gsheet():
    # On utilise l'URL stockée dans les secrets
    url = st.secrets["connections"]["gsheets"]["url"]
    # On passe par une méthode de lecture publique pour éviter l'erreur d'auth
    csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

# Pour l'écriture, si tu n'as pas de compte de service, 
# on va simuler la persistence avec le cache pour l'instant
if 'db' not in st.session_state:
    try:
        st.session_state.db = connect_gsheet()
    except:
        st.session_state.db = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type"])

# --- SIDEBAR VARIABLES ---
with st.sidebar:
    st.title("🛸 NAVIGATION")
    with st.expander("💰 CONFIGURATION REVENUS/CHARGES", expanded=False):
        sal = st.number_input("Salaire + Primes (€)", value=4238)
        charges = st.number_input("Total Charges Fixes (€)", value=2273)
        remboursement = st.number_input("Remboursement Découvert (€)", value=600)
        courses_max = st.slider("Budget Courses (€)", 300, 900, 600)
        active_agathe = st.toggle("Activer Agathe Budget", value=False)

# --- CALCULS ---
now = datetime.now()
jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
epargne_mensuelle = 1000 if active_agathe else 0
reste_mensuel = sal - charges - courses_max - remboursement - epargne_mensuelle
budget_jour_base = reste_mensuel / jours_dans_le_mois

# --- INTERFACE ---
st.title("🧬 Agathe Budget : Pilotage Odyssée")

tab1, tab2 = st.tabs(["⚡ DASHBOARD", "📑 HISTORIQUE"])

with tab1:
    aujourdhui = now.strftime("%Y-%m-%d")
    # Calcul des dépenses du jour dans l'état actuel
    df = st.session_state.db
    depenses_today = df[df["Date"] == aujourdhui]["Montant"].sum()
    dispo_aujourdhui = budget_jour_base - depenses_today
    
    col1, col2 = st.columns(2)
    col1.metric("OBJECTIF JOUR", f"{budget_jour_base:.2f} €")
    col2.metric("RESTE RÉEL", f"{dispo_aujourdhui:.2f} €")
    
    st.divider()
    with st.form("ajout"):
        n = st.text_input("Nom de l'achat")
        m = st.number_input("Montant (€)", min_value=0.0)
        if st.form_submit_button("🔨 Enregistrer l'opération"):
            new_entry = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": "Vie"}])
            st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
            st.success("Opération ajoutée (mémoire locale)")
            st.rerun()

with tab2:
    st.subheader("Historique des dépenses")
    st.dataframe(st.session_state.db.sort_values(by="Date", ascending=False), use_container_width=True)
    
    st.info("💡 Pour une sauvegarde permanente sur Google Sheets, il est recommandé d'utiliser un 'Service Account'.")

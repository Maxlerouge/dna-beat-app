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
    .stButton>button { width: 100%; border-radius: 25px; border: 1px solid #00f2fe; background: transparent; color: #00f2fe; }
    .discipline-score { font-size: 2.5rem; text-align: center; color: #00f2fe; font-weight: bold; text-shadow: 0 0 10px #00f2fe; }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="Historique", ttl=0)
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

# --- INITIALISATION MÉMOIRE ---
if 'solde_reporte' not in st.session_state: st.session_state.solde_reporte = 0.0
if 'tresor_agathe' not in st.session_state: st.session_state.tresor_agathe = 0.0

# --- SIDEBAR : TOUTES LES VARIABLES ---
with st.sidebar:
    st.title("🛸 NAVIGATION")
    mode_urgence = st.toggle("🚨 MODE URGENCE", value=False)
    
    with st.expander("💰 REVENUS (Instituteur)", expanded=False):
        sal = st.number_input("Salaire base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer perçu (€)", value=588)
        h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    with st.expander("🏠 CHARGES FIXES (IRL incluse)", expanded=False):
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
total_rev = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_agathe = 1000 if active_agathe else 0

# Impact Urgence
if mode_urgence: courses_prevues = courses_max * 0.7
else: courses_prevues = courses_max

reste_mensuel = total_rev - total_charges - courses_prevues - remboursement - epargne_agathe
budget_jour_base = reste_mensuel / jours_dans_le_mois

# --- INTERFACE ---
st.title("🧬 Agathe Budget : Forteresse")

tab1, tab2, tab3 = st.tabs(["⚡ PILOTAGE", "📑 HISTORIQUE", "💎 TRÉSOR"])

with tab1:
    df_h = load_data()
    aujourdhui = now.strftime("%Y-%m-%d")
    depenses_today = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    # Score Discipline
    budget_theorique_cumule = budget_jour_base * now.day
    total_depense_mois = df_h["Montant"].sum()
    score = max(0, min(100, int(100 - (total_depense_mois / (budget_theorique_cumule + 1) * 20))))

    c1, c2, c3 = st.columns(3)
    c1.metric("OBJECTIF JOUR", f"{budget_jour_base:.2f} €")
    c2.metric("RESTE RÉEL", f"{dispo_aujourdhui:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} Report")
    with c3:
        st.markdown(f"<div class='discipline-score'>{score}%</div>", unsafe_allow_html=True)
        st.caption("<p style='text-align:center;'>Discipline</p>", unsafe_allow_html=True)

    st.divider()
    with st.form("add"):
        col1, col2 = st.columns(2)
        n = col1.text_input("Désignation")
        m = col2.number_input("Montant (€)", min_value=0.0)
        if st.form_submit_button("🔨 ENREGISTRER (Google Sheets)"):
            new_entry = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": "Vie", "Mode": "Urgence" if mode_urgence else "Normal"}])
            updated_df = pd.concat([df_h, new_entry], ignore_index=True)
            conn.update(worksheet="Historique", data=updated_df)
            st.rerun()

    if st.button("🌙 Clôturer & Reporter"):
        st.session_state.solde_reporte = dispo_aujourdhui
        if active_agathe: st.session_state.tresor_agathe += (1000 / jours_dans_le_mois)
        st.rerun()
    
    if st.button("🔄 Reset Journée"):
        st.session_state.solde_reporte = 0.0
        st.rerun()

with tab2:
    st.subheader("Archives Mobiles")
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🗑️ Reset Historique (Action Irréversible)"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.rerun()

with tab3:
    st.subheader("Capital Agathe")
    st.metric("Trésor", f"{st.session_state.tresor_agathe:.2f} €")
    st.progress(min(1.0, st.session_state.tresor_agathe / 10000))
    if st.button("🏁 Reset Trésor"):
        st.session_state.tresor_agathe = 0.0
        st.rerun()

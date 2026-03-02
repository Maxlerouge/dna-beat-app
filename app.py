import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de l'interface
st.set_page_config(page_title="DNA-Beat Dashboard", page_icon="🧬", layout="wide")

# --- DESIGN CUSTOM (Version compatible) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1f77b4; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE ---
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'depenses_jour' not in st.session_state:
    st.session_state.depenses_jour = []
if 'tresor_dna' not in st.session_state:
    st.session_state.tresor_dna = 0.0

st.title("🧬 DNA-Beat Pilotage")

# --- SIDEBAR : CONTRÔLE TOTAL ---
with st.sidebar:
    st.header("💰 REVENUS")
    sal = st.number_input("Salaire de base (€)", value=3500)
    caaf = st.number_input("CAAF (€)", value=150)
    loyer_in = st.number_input("Loyer perçu (€)", value=588)
    h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    st.header("🏠 CHARGES FIXES")
    loyer_out = st.number_input("Loyer emprunt (€)", value=850)
    assu_emp = st.number_input("Assurance emprunt (€)", value=200)
    tel_net = st.number_input("Tel + Internet (€)", value=90)
    edf_eau = st.number_input("EDF + Eau (€)", value=298)
    mgen = st.number_input("MGEN (€)", value=160)
    voiture = st.number_input("Kona + Assurance (€)", value=415)
    famille = st.number_input("Enfants / Cantine (€)", value=200)
    divers = st.number_input("Autres (Drive/Vie) (€)", value=110)
    
    st.header("🎯 STRATÉGIE")
    decouvert_init = st.number_input("Découvert début (€)", value=-2000)
    remboursement_mensuel = st.number_input("Remboursement (€)", value=600)
    courses = st.slider("Budget Courses (€)", 300, 900, 600)
    active_dna = st.toggle("Épargne DNA-Beat (1000€)", value=False)

# --- CALCULS ---
total_revenus = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_mois = 1000 if active_dna else 0

reste_mensuel_vie = total_revenus - total_charges - courses - remboursement_mensuel - epargne_mois
budget_jour_base = reste_mensuel_vie / 30

# --- INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📱 AUJOURD'HUI", "💸 SAISIE", "📈 BILAN"])

with tab1:
    depenses_actuelles = sum(d['Montant'] for d in st.session_state.depenses_jour)
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_actuelles
    
    col1, col2 = st.columns(2)
    col1.metric("Objectif Jour", f"{budget_jour_base:.2f} €")
    col2.metric("Report Veille", f"{st.session_state.solde_reporte:.2f} €")
    
    st.write("---")
    if dispo_aujourdhui < 0:
        st.markdown(f"<h1 style='text-align: center; color: #d9534f;'>{dispo_aujourdhui:.2f} €</h1>", unsafe_allow_html=True)
        st.error("Budget dépassé ! Le surplus sera déduit de demain.")
    else:
        st.markdown(f"<h1 style='text-align: center; color: #5cb85c;'>{dispo_aujourdhui:.2f} €</h1>", unsafe_allow_html=True)
        st.success("Tu es dans les clous ! L'économie sera ajoutée à demain.")

    if st.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = dispo_aujourdhui
        st.session_state.depenses_jour = []
        if active_dna:
            st.session_state.tresor_dna += (1000/30)
        st.rerun()

with tab2:
    with st.form("depense"):
        nom = st.text_input("Nom de l'achat")
        montant = st.number_input("Montant (€)", min_value=0.0)
        if st.form_submit_button("Aj

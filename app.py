import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

# --- CONFIGURATION & DESIGN FUTURISTE ---
st.set_page_config(page_title="DNA-Beat Odyssée", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    /* Fond sombre et texte clair */
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    
    /* Cartes Néon */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 255, 255, 0.1);
    }
    
    /* Boutons stylisés */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        border: 1px solid #00f2fe;
        background: transparent;
        color: #00f2fe;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #00f2fe;
        color: #000;
        box-shadow: 0 0 20px #00f2fe;
    }
    
    /* Titres */
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- MÉMOIRE INTERNE ---
if 'historique' not in st.session_state:
    st.session_state.historique = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type"])
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'tresor_dna' not in st.session_state:
    st.session_state.tresor_dna = 0.0

# --- SIDEBAR : CONTRÔLE TOTAL DES VARIABLES ---
with st.sidebar:
    st.title("🛸 NAVIGATION")
    mode_urgence = st.toggle("🚨 MODE URGENCE", value=False)
    
    with st.expander("💰 REVENUS RÉELS", expanded=False):
        sal = st.number_input("Salaire base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer perçu (€)", value=588)
        h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    with st.expander("🏠 CHARGES DÉTAILLÉES", expanded=False):
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
        active_dna = st.toggle("Activer DNA-Beat", value=False)

# --- CALCULS ---
now = datetime.now()
jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
total_rev = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_dna_mensuelle = 1000 if active_dna else 0
reste_mensuel = total_rev - total_charges - courses_max - remboursement - epargne_dna_mensuelle
budget_jour_base = reste_mensuel / jours_dans_le_mois

# --- INTERFACE PRINCIPALE ---
st.title("🧬 DNA-Beat : Pilotage Odyssée")

tab1, tab2, tab3 = st.tabs(["⚡ DASHBOARD", "📑 HISTORIQUE", "💎 TRÉSOR DNA"])

with tab1:
    # Calcul du jour
    aujourdhui = now.strftime("%Y-%m-%d")
    depenses_today = st.session_state.historique[st.session_state.historique["Date"] == aujourdhui]["Montant"].sum()
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    c1, c2 = st.columns(2)
    c1.metric("OBJECTIF JOUR", f"{budget_jour_base:.2f} €")
    c2.metric("RESTE RÉEL", f"{dispo_aujourdhui:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} (Report)")
    
    st.divider()
    if st.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = dispo_aujourdhui
        if active_dna: st.session_state.tresor_dna += (1000 / jours_dans_le_mois)
        st.rerun()
    
    if st.button("🔄 Reset Journée", help="Remet à zéro le report et les dépenses du jour"):
        st.session_state.solde_reporte = 0.0
        st.rerun()

with tab2:
    st.subheader("Saisie & Historique")
    with st.form("saisie_v4"):
        col1, col2 = st.columns(2)
        n = col1.text_input("Désignation")
        m = col2.number_input("Montant (€)", min_value=0.0)
        if st.form_submit_button("🔨 Enregistrer"):
            new = pd.DataFrame({"Date": [aujourdhui], "Nom": [n], "Montant": [m], "Type": ["Variable"]})
            st.session_state.historique = pd.concat([st.session_state.historique, new], ignore_index=True)
            st.rerun()
            
    st.dataframe(st.session_state.historique.sort_values(by="Date", ascending=False), use_container_width=True)
    
    if st.button("🗑️ Reset Historique", help="Efface toutes les opérations enregistrées"):
        st.session_state.historique = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type"])
        st.rerun()

with tab3:
    st.subheader("Capital DNA-Beat")
    st.metric("Trésor Accumulé", f"{st.session_state.tresor_dna:.2f} €")
    st.progress(min(1.0, st.session_state.tresor_dna / 10000))
    
    st.divider()
    if st.button("🏁 Reset Trésor", help="Remet le capital DNA-Beat à zéro"):
        st.session_state.tresor_dna = 0.0
        st.rerun()

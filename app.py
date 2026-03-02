import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(page_title="DNA-Beat App", page_icon="🧬", layout="wide")

# Initialisation des bases de données internes
if 'historique' not in st.session_state:
    st.session_state.historique = pd.DataFrame(columns=["Date", "Nom", "Montant"])
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'tresor_dna' not in st.session_state:
    st.session_state.tresor_dna = 0.0

st.title("🧬 DNA-Beat : Pilotage d'État")

# --- SIDEBAR : TOUS TES PARAMÈTRES (MODIFIABLES) ---
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
    divers = st.number_input("Autres (Abo/Vie) (€)", value=110)
    
    st.header("🎯 STRATÉGIE")
    remboursement_decouvert = st.number_input("Remboursement mensuel (€)", value=600)
    courses_prevues = st.slider("Budget Courses (€)", 300, 900, 600)
    active_dna = st.toggle("Épargne DNA-Beat (1000€)", value=False)

# --- CALCULS DE STRUCTURE ---
total_revenus = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_mois = 1000 if active_dna else 0
reste_mensuel_vie = total_revenus - total_charges - courses_prevues - remboursement_decouvert - epargne_mois
budget_jour_base = reste_mensuel_vie / 30

# --- INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📱 AUJOURD'HUI", "📜 HISTORIQUE", "📈 PROJET DNA-BEAT"])

with tab1:
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    df_h = st.session_state.historique
    depenses_today = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
    
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    c1, c2 = st.columns(2)
    c1.metric("Base Jour", f"{budget_jour_base:.2f} €")
    c2.metric("Report Veille", f"{st.session_state.solde_reporte:.2f} €")
    
    color_code = "#5cb85c" if dispo_aujourdhui >= 0 else "#d9534f"
    st.markdown(f"<h1 style='text-align: center; color: {color_code};'>{dispo_aujourdhui:.2f} €</h1>", unsafe_allow_html=True)

    with st.expander("💸 Ajouter une dépense"):
        with st.form("ajout"):
            n = st.text_input("Nom de l'achat")
            m = st.number_input("Montant (€)", min_value=0.0, step=1.0)
            d = st.date_input("Date", datetime.now())
            if st.form_submit_button("Valider"):
                new = pd.DataFrame({"Date": [d.strftime("%Y-%m-%d")], "Nom": [n], "Montant": [m]})
                st.session_state.historique = pd.concat([st.session_state.historique, new], ignore_index=True)
                st.rerun()

    if st.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = dispo_aujourdhui
        if active_dna: st.session_state.tresor_dna += (1000/30)
        st.balloons()
        st.rerun()

with tab2:
    st.subheader("Toutes tes opérations")
    if not st.session_state.historique.empty:
        st.dataframe(st.session_state.historique.sort_values(by="Date", ascending=False), use_container_width=True)
        if st.button("Supprimer la dernière ligne"):
            st.session_state.historique = st.session_state.historique.iloc[:-1]
            st.rerun()
    else:
        st.info("Aucun historique pour le moment.")

with tab3:
    st.subheader("Accumulation DNA-Beat")
    st.metric("Trésor Cumulé", f"{st.session_state.tresor_dna:.2f} €")
    st.progress(min(1.0, st.session_state.tresor_dna / 10000))
    
    st.divider()
    if st.button("🔄 Nouveau Mois (Reset)"):
        st.session_state.solde_reporte = 0.0
        st.rerun()

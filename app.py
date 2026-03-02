import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de l'interface
st.set_page_config(page_title="DNA-Beat Dashboard", page_icon="🧬", layout="wide")

# --- DESIGN CUSTOM ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_url_path=True)

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'depenses_jour' not in st.session_state:
    st.session_state.depenses_jour = []
if 'tresor_dna' not in st.session_state:
    st.session_state.tresor_dna = 0.0

st.title("🧬 DNA-Beat : Pilotage Intelligent")

# --- SIDEBAR : CONTRÔLE TOTAL ---
with st.sidebar:
    st.header("💰 REVENUS")
    sal = st.number_input("Salaire de base (€)", value=3500)
    caaf = st.number_input("CAAF (€)", value=150)
    loyer_in = st.number_input("Loyer perçu (€)", value=588)
    h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    st.header("🏠 TOUTES LES CHARGES")
    loyer_out = st.number_input("Loyer emprunt (€)", value=850)
    assu_emp = st.number_input("Assurance emprunt (€)", value=200)
    tel_net = st.number_input("Tel + Internet (€)", value=90)
    edf_eau = st.number_input("EDF + Eau (€)", value=298)
    mgen = st.number_input("MGEN (€)", value=160)
    voiture = st.number_input("Kona + Assurance (€)", value=415)
    famille = st.number_input("Enfants / Cantine (€)", value=200)
    divers = st.number_input("Autres (Drive/Vie/Assu) (€)", value=110)
    
    st.header("🎯 STRATÉGIE")
    decouvert_init = st.number_input("Découvert début mois (€)", value=-2000)
    remboursement_mensuel = st.number_input("Remboursement fixé (€)", value=600)
    courses = st.slider("Budget Courses (€)", 300, 900, 600)
    active_dna = st.toggle("Épargne DNA-Beat (1000€)", value=False)

# --- CALCULS DE BASE ---
total_revenus = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_mois = 1000 if active_dna else 0

reste_mensuel_vie = total_revenus - total_charges - courses - remboursement_mensuel - epargne_mois
budget_jour_theorique = reste_mensuel_vie / 30

# --- INTERFACE PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["🚀 AUJOURD'HUI", "💸 SAISIE DÉPENSE", "📈 BILAN & TRÉSOR"])

with tab1:
    st.subheader("État de ton budget quotidien")
    
    # Calcul du Reste Réel avec report
    depenses_actuelles = sum(d['Montant'] for d in st.session_state.depenses_jour)
    budget_du_jour_avec_report = budget_jour_theorique + st.session_state.solde_reporte
    reste_final = budget_du_jour_avec_report - depenses_actuelles
    
    # Affichage visuel
    c1, c2, c3 = st.columns(3)
    c1.metric("Base Jour", f"{budget_jour_theorique:.2f} €")
    
    # Report de la veille (couleur bleue si positif, orange si négatif)
    c2.metric("Report de la veille", f"{st.session_state.solde_reporte:.2f} €")
    
    # LE RESTE RÉEL (Rouge si négatif)
    if reste_final < 0:
        st.error(f"⚠️ ATTENTION : Tu es à {reste_final:.2f} €")
    else:
        st.success(f"✅ DISPONIBLE : {reste_final:.2f} €")
    
    st.divider()
    
    # Bouton Fin de Journée (C'est ici que la magie du report opère)
    if st.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = reste_final # Le reste devient le report de demain
        st.session_state.depenses_jour = []
        if active_dna:
            st.session_state.tresor_dna += (1000/30) # On simule l'accumulation quotidienne
        st.rerun()

with tab2:
    st.subheader("Ajouter un achat")
    with st.form("depense"):
        nom = st.text_input("Nom de la dépense")
        montant = st.number_input("Montant (€)", min_value=0.0)
        if st.form_submit_button("Enregistrer"):
            if nom and montant > 0:
                st.session_state.depenses_jour.append({"Nom": nom, "Montant": montant, "Heure": datetime.now().strftime("%H:%M")})
                st.rerun()
    
    if st.session_state.depenses_jour:
        st.write("Dépenses du jour :")
        st.table(pd.DataFrame(st.session_state.depenses_jour))

with tab3:
    st.subheader("Bilan du Projet DNA-Beat")
    
    # Jauge de remboursement découvert
    nouveau_decouvert = decouvert_init + remboursement_mensuel
    st.write(f"📉 **Découvert estimé fin de mois : {nouveau_decouvert:.2f} €**")
    st.progress(min(1.0, max(0.0, (2000 + nouveau_decouvert) / 2000)))
    
    st.divider()
    
    # JAUGE DE TRÉSOR DNA-BEAT
    st.subheader("💎 Trésor Cumulé DNA-Beat")
    st.write(f"Ton capital pour le projet : **{st.session_state.tresor_dna:.2f} €**")
    st.progress(min(1.0, st.session_state.tresor_dna / 10000)) # Jauge sur un objectif de 10k€
    
    if st.button("Reset Mensuel (Nouveau Salaire)"):
        st.session_state.solde_reporte = 0.0
        st.rerun()

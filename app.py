import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="DNA-Beat Pilotage", page_icon="🧬")

# --- INITIALISATION DES MÉMOIRES ---
if 'depenses_jour' not in st.session_state:
    st.session_state.depenses_jour = []
if 'total_depense_mois' not in st.session_state:
    st.session_state.total_depense_mois = 0.0

st.title("🧬 DNA-Beat : Pilotage Intégral")

# --- BARRE LATÉRALE : CONFIGURATION DU MOIS ---
st.sidebar.header("⚙️ PARAMÈTRES DU MOIS")
h_sup = st.sidebar.number_input("Heures Sup' (€)", value=500)
courses_budget = st.sidebar.slider("Budget Courses (€)", 300, 800, 600)
active_dna = st.sidebar.toggle("Épargne DNA-Beat (1000€)", value=False)
decouvert_depart = st.sidebar.number_input("Découvert début de mois (€)", value=-2000.0)

# CALCULS FIXES (Basés sur tes données d'Instituteur d'État)
revenus_fixes = 4238 # Salaire + CAAF + Loyer perçu
charges_fixes = 2273
remboursement_fixe = 600
epargne_dna = 1000 if active_dna else 0

# Calcul du Reste Mensuel Théorique
revenus_totaux = revenus_fixes + h_sup
reste_mensuel_theorique = revenus_totaux - charges_fixes - courses_budget - remboursement_fixe - epargne_dna
budget_jour_theorique = reste_mensuel_theorique / 30

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📱 AUJOURD'HUI", "💸 SAISIE", "📊 BILAN MENSUEL"])

with tab1:
    # Calcul du jour
    total_jour = sum(d['Montant'] for d in st.session_state.depenses_jour)
    reste_reel_jour = budget_jour_theorique - total_jour
    
    st.subheader("Ton budget du jour")
    c1, c2 = st.columns(2)
    c1.metric("Objectif / Jour", f"{budget_jour_theorique:.2f} €")
    color = "normal" if reste_reel_jour >= 0 else "inverse"
    c2.metric("RESTE RÉEL", f"{reste_reel_jour:.2f} €", delta=f"-{total_jour:.2f} €", delta_color=color)

    if reste_reel_jour < 0:
        st.error("⚠️ Tu as dépassé ton budget quotidien !")
    
    # Liste des dépenses du jour
    if st.session_state.depenses_jour:
        st.write("---")
        st.dataframe(pd.DataFrame(st.session_state.depenses_jour), use_container_width=True)
        if st.button("Finir la journée 🌙"):
            # On ajoute le total du jour au cumul du mois avant d'effacer
            st.session_state.total_depense_mois += total_jour
            st.session_state.depenses_jour = []
            st.success("Journée clôturée et ajoutée au mois !")
            st.rerun()

with tab2:
    st.subheader("Nouvelle dépense")
    with st.form("ajout"):
        nom = st.text_input("Qu'as-tu acheté ?")
        prix = st.number_input("Montant (€)", min_value=0.0, step=1.0)
        if st.form_submit_button("Valider"):
            if nom:
                st.session_state.depenses_jour.append({"Heure": datetime.now().strftime("%H:%M"), "Nom": nom, "Montant": prix})
                st.rerun()

with tab3:
    st.subheader("Suivi de ton mois")
    
    # État du découvert
    nouveau_decouvert = decouvert_depart + remboursement_fixe
    st.write(f"📉 **Découvert estimé en fin de mois : {nouveau_decouvert:.2f} €**")
    st.progress(min(1.0, max(0.0, (2000 + nouveau_decouvert) / 2000)))

    # État des dépenses "Reste pour la vie"
    st.write("---")
    st.write(f"💰 **Cumul des dépenses plaisir ce mois : {st.session_state.total_depense_mois:.2f} €**")
    budget_total_mois = reste_mensuel_theorique
    reste_sur_le_mois = budget_total_mois - st.session_state.total_depense_mois
    
    st.metric("Reste sur ton budget mensuel 'Vie'", f"{reste_sur_le_mois:.2f} €")
    
    if active_dna:
        st.success("💎 Ce mois-ci, tu as sécurisé 1000 € pour DNA-Beat !")
    else:
        st.info("🎯 Focus : Remboursement du découvert en priorité.")

    if st.button("Réinitialiser le mois (Nouveau Salaire)"):
        st.session_state.total_depense_mois = 0.0
        st.rerun()

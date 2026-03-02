import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="DNA-Beat V3", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .urgent { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    .discipline-score { font-size: 2rem; text-align: center; color: #1f77b4; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE ---
if 'historique' not in st.session_state:
    st.session_state.historique = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Urgence"])
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'tresor_dna' not in st.session_state:
    st.session_state.tresor_dna = 0.0

# --- CALCULS CALENDRIER ---
now = datetime.now()
jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
jours_ecoules = now.day

# --- SIDEBAR : PILOTAGE STRATÉGIQUE ---
with st.sidebar:
    st.title("🕹️ Cockpit V3")
    mode_urgence = st.toggle("🚨 MODE URGENCE (Survie)", value=False)
    
    st.divider()
    h_sup = st.number_input("Heures Sup' (€)", value=500)
    courses_max = st.slider("Budget Courses (€)", 300, 900, 600)
    active_dna = st.toggle("Projet DNA-Beat (1000€)", value=False)
    
    # Données fixes "Instituteur d'État"
    rev_fixes = 4238 
    charges_fixes = 2273 
    remboursement = 600
    
    total_rev = rev_fixes + h_sup
    epargne_dna_mois = 1000 if active_dna else 0
    
    # Impact Mode Urgence
    if mode_urgence:
        st.markdown("<div class='urgent'>MODE URGENCE ACTIVÉ : Loisirs bloqués</div>", unsafe_allow_html=True)
        courses_prevues = courses_max * 0.7 # Réduction forcée de 30%
    else:
        courses_prevues = courses_max

    reste_mensuel_vie = total_rev - charges_fixes - courses_prevues - remboursement - epargne_dna_mois
    budget_jour_base = reste_mensuel_vie / jours_dans_le_mois

# --- INTERFACE PRINCIPALE ---
st.title("🛡️ DNA-Beat : Forteresse Budgétaire")

tab1, tab2, tab3 = st.tabs(["🎯 PILOTAGE", "📝 OPÉRATIONS", "📊 ANALYSE"])

with tab1:
    # Calculs du jour
    aujourdhui = now.strftime("%Y-%m-%d")
    df_h = st.session_state.historique
    depenses_today = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    # --- SCORE DE DISCIPLINE ---
    # Somme des dépenses réelles vs Budget théorique cumulé
    budget_cumule_theorique = budget_jour_base * jours_ecoules
    depenses_totale_mois = df_h["Montant"].sum()
    score = max(0, min(100, int(100 - (depenses_totale_mois / (budget_cumule_theorique + 1) * 20))))
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Budget Jour", f"{budget_jour_base:.2f} €")
    with c2:
        st.metric("Dispo Réel", f"{dispo_aujourdhui:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} (Report)")
    with c3:
        st.markdown(f"<div class='discipline-score'>{score}%</div>", unsafe_allow_html=True)
        st.caption("<p style='text-align:center;'>Indice de Discipline</p>", unsafe_allow_html=True)

    st.divider()
    
    if dispo_aujourdhui < 0:
        st.error(f"Attention ! Tu as dépassé de {abs(dispo_aujourdhui):.2f} €. Demain sera amputé.")
    else:
        st.success(f"Tout est vert. {dispo_aujourdhui:.2f} € seront reportés à demain.")

    if st.button("🌙 Clôturer & Sauvegarder la journée"):
        st.session_state.solde_reporte = dispo_aujourdhui
        if active_dna: st.session_state.tresor_dna += (1000 / jours_dans_le_mois)
        st.balloons()
        st.rerun()

with tab2:
    with st.form("form_v3"):
        col_n, col_m, col_t = st.columns([2,1,1])
        nom = col_n.text_input("Désignation")
        montant = col_m.number_input("Montant (€)", min_value=0.0)
        type_op = col_t.selectbox("Catégorie", ["Vie", "Fixe", "Exceptionnel", "Loisir"])
        date_op = st.date_input("Date", now)
        
        if mode_urgence and type_op == "Loisir":
            st.warning("⚠️ Mode Urgence : Les loisirs sont déconseillés.")
            
        if st.form_submit_button("🔨 Valider l'opération"):
            if nom and montant > 0:
                new_data = pd.DataFrame({"Date": [date_op.strftime("%Y-%m-%d")], "Nom": [nom], "Montant": [montant], "Type": [type_op], "Urgence": [mode_urgence]})
                st.session_state.historique = pd.concat([st.session_state.historique, new_data], ignore_index=True)
                st.rerun()

with tab3:
    st.subheader("Trésor DNA-Beat")
    st.metric("Capital accumulé", f"{st.session_state.tresor_dna:.2f} €")
    st.progress(min(1.0, st.session_state.tresor_dna / 5000))
    
    st.divider()
    st.write("### Historique complet")
    st.dataframe(st.session_state.historique.sort_values(by="Date", ascending=False), use_container_width=True)

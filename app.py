import streamlit as st

st.set_page_config(page_title="DNA-Beat Pilotage", page_icon="🧬")

st.title("🧬 DNA-Beat : Ton Pilotage")

# --- LES ENTREES (MODIFIABLES) ---
st.sidebar.header("Tes variables du mois")
heures_sup = st.sidebar.slider("Heures Sup' (€)", 0, 1500, 500)
courses = st.sidebar.slider("Budget Courses (€)", 400, 800, 600)
phase = st.sidebar.selectbox("Phase actuelle", ["Remboursement Découvert", "Vitesse Croisière (DNA-Beat)"])

# --- LES CALCULS FIXES ---
revenus_fixes = 3500 + 150 + 588
charges_fixes = -2273 # Le total de tes 11 items détaillés

total_revenus = revenus_fixes + heures_sup
remboursement = -600 if phase == "Remboursement Découvert" else 0
epargne_dna = -1000 if phase == "Vitesse Croisière (DNA-Beat)" else 0

# --- LE CALCUL DU RESTE POUR LA VIE ---
reste_vie = total_revenus + charges_fixes + remboursement - courses + epargne_dna
budget_jour = reste_vie / 30

# --- AFFICHAGE ---
col1, col2 = st.columns(2)
col1.metric("Budget / Jour", f"{budget_jour:.2f} €")
col2.metric("Reste pour le mois", f"{reste_vie:.2f} €")

if phase == "Remboursement Découvert":
    st.warning(f"🎯 Objectif : Remboursement de 600€ en cours.")
    st.progress(0.3) # On peut lier ça au mois réel plus tard
else:
    st.success(f"🚀 DNA-Beat : 1000€ mis de côté ce mois-ci !")

st.info(f"Détail : Revenus {total_revenus}€ | Charges {abs(charges_fixes)}€")

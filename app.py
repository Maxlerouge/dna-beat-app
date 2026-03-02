import streamlit as st

# Configuration de la page pour mobile
st.set_page_config(page_title="DNA-Beat Pilotage", page_icon="🧬", layout="centered")

st.title("🧬 DNA-Beat : Pilotage Intégral")

# --- BARRE LATÉRALE : TOUTES TES VARIABLES ---
st.sidebar.header("💰 REVENUS")
sal_base = st.sidebar.number_input("Salaire de base (€)", value=3500)
caaf = st.sidebar.number_input("CAAF (€)", value=150)
loyer_percu = st.sidebar.number_input("Loyer perçu (€)", value=588)
h_sup = st.sidebar.slider("Heures Sup' (€)", 0, 1500, 500)

st.sidebar.header("🏠 CHARGES FIXES")
loyer_emprunt = st.sidebar.number_input("Loyer emprunt (€)", value=850)
assurance_emprunt = st.sidebar.number_input("Assurance emprunt (€)", value=200)
tel_net = st.sidebar.number_input("Tel + Internet (€)", value=90)
edf_eau = st.sidebar.number_input("EDF + Eau (€)", value=298)
mgen = st.sidebar.number_input("MGEN (€)", value=160)
divers_abo = st.sidebar.number_input("Abonnements (Drive/Assu) (€)", value=60)
voiture = st.sidebar.number_input("Kona + Assurance (€)", value=415)
enfants = st.sidebar.number_input("Enfants / Cantine (€)", value=200)
epargne_vie = st.sidebar.number_input("Assurance Vie (€)", value=50)

st.sidebar.header("📊 STRATÉGIE")
decouvert_actuel = st.sidebar.number_input("Découvert de départ (€)", value=-2000)
mode_remboursement = st.sidebar.toggle("Mode Remboursement (600€/mois)", value=True)
courses = st.sidebar.slider("Budget Courses (€)", 300, 800, 600)
active_dna = st.sidebar.toggle("Activer Épargne DNA-Beat (1000€)", value=False)

# --- CALCULS ---
total_revenus = sal_base + caaf + loyer_percu + h_sup
total_charges = (loyer_emprunt + assurance_emprunt + tel_net + edf_eau + 
                 mgen + divers_abo + voiture + enfants + epargne_vie)

# Gestion du remboursement et de l'épargne
remboursement = -600 if mode_remboursement else 0
epargne_dna = -1000 if active_dna else 0

# Calcul final du reste pour vivre
reste_mensuel = total_revenus - total_charges + remboursement - courses + epargne_dna
budget_jour = reste_mensuel / 30

# --- AFFICHAGE SUR L'APP ---

# 1. Les indicateurs clés
col1, col2 = st.columns(2)
with col1:
    st.metric("Budget / Jour", f"{budget_jour:.2f} €")
with col2:
    st.metric("Reste Mensuel", f"{reste_mensuel:.2f} €")

# 2. Barre de progression du découvert
st.subheader("📉 Suivi du Découvert")
nouveau_solde = decouvert_actuel - remboursement
progres = min(1.0, max(0.0, (2000 + nouveau_solde) / 2000))
st.progress(progres)
st.write(f"Solde estimé fin de mois : **{nouveau_solde:.2f} €**")

# 3. Alertes visuelles
if budget_jour < 25:
    st.error("⚠️ Budget serré ! Attention aux extras.")
elif budget_jour > 40:
    st.success("✅ Confortable ! Tu peux épargner un peu plus.")
else:
    st.info("👍 Budget équilibré.")

# 4. Récapitulatif
with st.expander("Voir le détail du calcul"):
    st.write(f"Revenus : {total_revenus} €")
    st.write(f"Charges : -{total_charges} €")
    st.write(f"Courses : -{courses} €")
    if active_dna:
        st.write("Épargne DNA-Beat : -1000 €")

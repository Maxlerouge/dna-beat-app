import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Agathe Budget | DNA-Beat", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e); color: #e0e0e0; }
    [data-testid="stMetric"] { background: rgba(0, 242, 254, 0.05); border-left: 5px solid #00f2fe; border-radius: 10px; padding: 15px; }
    .stButton>button { width: 100%; border-radius: 20px; border: 1px solid #00f2fe; background: transparent; color: #00f2fe; font-weight: bold; }
    .stButton>button:hover { background: #00f2fe; color: #1a1a2e; box-shadow: 0 0 20px #00f2fe; }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 8px rgba(0, 242, 254, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION CLOUD ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name="Historique"):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
        df["Montant"] = pd.to_numeric(df["Montant"], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

# --- MÉMOIRE SOLDE ---
if 'solde_ajustement' not in st.session_state: st.session_state.solde_ajustement = 0.0

# --- SIDEBAR : TOUTES LES VARIABLES ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("Projet DNA-Beat | v7.4")
    
    with st.expander("💰 REVENUS (Modifiables)", expanded=False):
        sal = st.number_input("Salaire Base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer Perçu (€)", value=588)
        h_sup = st.number_input("Heures Sup (€)", value=500)
        rev_extra = st.number_input("Revenu Supplémentaire (€)", value=0.0)
    
    with st.expander("⚙️ AJUSTEMENT SOLDE BANQUE", expanded=True):
        st.session_state.solde_ajustement = st.number_input("Ajustement / Report (€)", value=st.session_state.solde_ajustement)

    with st.expander("🏠 CHARGES FIXES (Modifiables)", expanded=False):
        l_out = st.number_input("Loyer / Emprunt (€)", value=850)
        a_emp = st.number_input("Assurance Emprunt (€)", value=200)
        t_net = st.number_input("Tel + Internet (€)", value=90)
        e_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        kona = st.number_input("Kona + Assurance (€)", value=415)
        fam = st.number_input("Famille / Enfants (€)", value=200)
        a_vie = st.number_input("Assurance Vie (€)", value=50) # Variable Assurance Vie

    with st.expander("📉 DÉCOUVERT & STRATÉGIE", expanded=True):
        remboursement = st.number_input("Remboursement ce mois (€)", value=600) # Réglé à 600
        obj_decouvert = st.number_input("Découvert Total (Cible)", value=2000) # Cible 2000
        budget_bouffe = st.slider("Budget Courses / Bouffe (€)", 300, 1000, 600) # Curseur Bouffe
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=False)
        mode_urgence = st.toggle("🚨 MODE VIGILANCE", value=False)

# --- LOGIQUE DE CALCUL ---
now = datetime.now()
jours_dans_mois = calendar.monthrange(now.year, now.month)[1]

# Calculs totaux
rev_total = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie
epargne_agathe = 1000 if active_agathe else 0
coeff_urg = 0.7 if mode_urgence else 1.0

# Budget mensuel restant après obligations
# (Revenus - Charges - Remboursement - Epargne - Budget Courses réservé)
budget_restant_mois = rev_total - charges_total - remboursement - epargne_agathe - (budget_bouffe * coeff_urg)
obj_journalier = budget_restant_mois / jours_dans_mois

# --- DASHBOARD PRINCIPAL ---
st.title(f"💎 Pilotage Agathe Budget : {now.strftime('%B %Y')}")

df_h = load_data()
total_depense_mois = df_h["Montant"].sum()
aujourdhui = now.strftime("%Y-%m-%d")
depense_jour = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()

# Calcul du disponible réel du jour
reste_reel_jour = obj_journalier + st.session_state.solde_ajustement - depense_jour

c1, c2, c3 = st.columns(3)
c1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
c2.metric("DISPONIBLE RÉEL", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_ajustement:.2f} Ajusté")
c3.metric("PRÉVISION FIN MOIS", f"{(budget_restant_mois + st.session_state.solde_ajustement) - total_depense_mois:.2f} €")

st.divider()

# --- ANALYSE ET GRAPHIQUES ---
col_graph, col_stat = st.columns([2, 1])

with col_graph:
    st.subheader("🧬 Évolution des Dépenses")
    if not df_h.empty:
        df_daily = df_h.groupby("Date")["Montant"].sum().reset_index()
        fig = px.area(df_daily, x="Date", y="Montant", color_discrete_sequence=["#00f2fe"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun achat enregistré pour le moment.")

with col_stat:
    st.subheader("🎯 Progression")
    # Barre de progression du remboursement
    p_decouvert = min(1.0, (remboursement / (obj_decouvert if obj_decouvert > 0 else 1)))
    st.write(f"Remboursement : {remboursement}€ / {obj_decouvert}€")
    st.progress(p_decouvert)
    
    if not df_h.empty:
        fig2 = px.pie(df_h, values='Montant', names='Type', hole=.5, color_discrete_sequence=px.colors.sequential.Teal)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- ONGLETS D'ACTIONS ---
tab_saisie, tab_histo, tab_options = st.tabs(["✍️ SAISIR ACHAT", "📑 HISTORIQUE", "⚙️ ARCHIVES & TRESOR"])

with tab_saisie:
    with st.form("form_saisie"):
        ca, cb, cc = st.columns([2,1,1])
        nom_achat = ca.text_input("Désignation")
        montant_achat = cb.number_input("Montant (€)", min_value=0.0, step=0.01)
        type_achat = cc.selectbox("Catégorie", ["Vie Courante", "Courses", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 ENREGISTRER L'ACHAT"):
            if nom_achat and montant_achat > 0:
                new_data = pd.DataFrame([{"Date": aujourdhui, "Nom": nom_achat, "Montant": montant_achat, "Type": type_achat, "Mode": "Urgence" if mode_urgence else "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_data], ignore_index=True))
                st.balloons()
                st.rerun()

with tab_histo:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer Journée (Reporter le solde)"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with tab_options:
    st.subheader("💎 Trésor & Patrimoine")
    st.write(f"Assurance Vie : {a_vie} € (Déduit)")
    st.write(f"Trésor Agathe : {epargne_agathe} € (Déduit)")
    
    st.divider()
    st.subheader("🛡️ Sauvegarde")
    if st.button("📦 SAUVEGARDER VERS L'ONGLET ARCHIVES"):
        try:
            df_arch = load_data("Archives")
            conn.update(worksheet="Archives", data=pd.concat([df_arch, df_h], ignore_index=True))
            st.success("Données archivées avec succès !")
        except:
            st.error("Erreur : Créez l'onglet 'Archives' dans votre Google Sheet.")

    if st.button("🗑️ REMISE À ZÉRO DU MOIS"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.session_state.solde_ajustement = 0.0
        st.rerun()

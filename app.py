import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Agathe Budget | Pilotage", page_icon="💎", layout="wide")

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

def load_data():
    try:
        df = conn.read(worksheet="Historique", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
        df["Montant"] = pd.to_numeric(df["Montant"], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

# --- SESSION STATE ---
if 'solde_reporte' not in st.session_state: st.session_state.solde_reporte = 0.0

# --- SIDEBAR : PILOTAGE AGATHE ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("DNA-Beat v6.6 | 2026")
    mode_urgence = st.toggle("🚨 MODE VIGILANCE RAPPROCHÉE", value=False)
    
    with st.expander("💰 REVENUS DÉTAILLÉS", expanded=False):
        sal = st.number_input("Salaire Base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer Perçu (€)", value=588)
        h_sup = st.number_input("Heures Sup (€)", value=500)
    
    with st.expander("🏠 CHARGES FIXES DÉTAILLÉES", expanded=False):
        l_out = st.number_input("Loyer / Emprunt (€)", value=850)
        a_emp = st.number_input("Assurance Emprunt (€)", value=200)
        t_net = st.number_input("Tel + Internet (€)", value=90)
        e_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        kona = st.number_input("Kona + Assurance (€)", value=415)
        fam = st.number_input("Famille / Enfants (€)", value=200)
        div = st.number_input("Divers / Autres (€)", value=110)
        
    with st.expander("📉 GESTION DÉCOUVERT", expanded=True):
        decouvert_mensuel = st.number_input("Remboursement ce mois (€)", value=600)
        objectif_decouvert = st.number_input("Découvert total à combler (€)", value=2000)

    with st.expander("🎯 STRATÉGIE ÉPARGNE", expanded=True):
        courses_budget = st.slider("Budget Courses (€)", 300, 900, 600)
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=False)

# --- CALCULS ---
now = datetime.now()
jours_mois = calendar.monthrange(now.year, now.month)[1]

# Revenus sans IRL
rev_total = sal + caaf + loyer_in + h_sup
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + div
epargne_auto = 1000 if active_agathe else 0
coeff_urgence = 0.7 if mode_urgence else 1.0

budget_dispo_mois = rev_total - charges_total - decouvert_mensuel - epargne_auto - (courses_budget * coeff_urgence)
obj_journalier = budget_dispo_mois / jours_mois

# --- INTERFACE ---
st.title(f"💎 Agathe Budget : {now.strftime('%B %Y')}")

df_h = load_data()
total_depense_mois = df_h["Montant"].sum()
aujourdhui = now.strftime("%Y-%m-%d")
depense_jour = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
reste_reel_jour = obj_journalier + st.session_state.solde_reporte - depense_jour

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
with c2:
    st.metric("DISPONIBLE AUJOURD'HUI", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} Reporté")
with c3:
    projection = budget_dispo_mois - total_depense_mois
    st.metric("SOLDE PRÉVISIONNEL", f"{projection:.2f} €")

st.markdown("---")

# --- GRAPHIQUES ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🧬 Courbe des Dépenses")
    if not df_h.empty:
        df_daily = df_h.groupby("Date")["Montant"].sum().reset_index()
        fig = px.line(df_daily, x="Date", y="Montant", markers=True, color_discrete_sequence=["#00f2fe"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("En attente de données...")

with col_right:
    st.subheader("🎯 Suivi Découvert")
    progression_decouvert = min(1.0, (decouvert_mensuel / (objectif_decouvert if objectif_decouvert > 0 else 1)))
    st.progress(progression_decouvert)
    st.write(f"Remboursement : {decouvert_mensuel}€ / {objectif_decouvert}€")
    
    if not df_h.empty:
        fig2 = px.pie(df_h, values='Montant', names='Type', hole=.5, color_discrete_sequence=px.colors.sequential.Teal)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- ACTIONS ---
tab_saisie, tab_histo, tab_tresor = st.tabs(["✍️ NOUVEL ACHAT", "📑 HISTORIQUE", "💎 TRÉSOR AGATHE"])

with tab_saisie:
    with st.form("form_saisie"):
        c_a, c_b, c_c = st.columns([2,1,1])
        n = c_a.text_input("Désignation")
        m = c_b.number_input("Montant (€)", min_value=0.0, step=0.01)
        t = c_c.selectbox("Catégorie", ["Vie Courante", "Courses", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 ENREGISTRER SUR LE CLOUD"):
            if n and m > 0:
                new_l = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": t, "Mode": "Urgence" if mode_urgence else "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_l], ignore_index=True))
                st.balloons()
                st.rerun()

with tab_histo:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    cb1, cb2, cb3 = st.columns(3)
    if cb1.button("🌙 Clôturer Journée"):
        st.session_state.solde_reporte = reste_reel_jour
        st.rerun()
    if cb2.button("🔄 Reset Report"):
        st.session_state.solde_reporte = 0.0
        st.rerun()
    if cb3.button("🗑️ Vider Historique"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.rerun()

with tab_tresor:
    st.subheader("💰 Capital Sécurisé")
    st.metric("Trésor Agathe Prévu", f"{epargne_auto:.2f} €")
    st.write("Ce montant est prélevé sur votre budget pour garantir votre épargne.")

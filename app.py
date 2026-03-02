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

# --- CONNEXION ---
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

# --- SESSION STATE ---
if 'solde_ajustement' not in st.session_state: st.session_state.solde_ajustement = 0.0

# --- SIDEBAR : PILOTAGE COMPLET ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("DNA-Beat v7.1 | Perfection")
    
    with st.expander("💰 REVENUS", expanded=False):
        sal = st.number_input("Salaire Base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer Perçu (€)", value=588)
        h_sup = st.number_input("Heures Sup (€)", value=500)
        rev_extra = st.number_input("Revenu Supplémentaire (€)", value=0.0)
    
    with st.expander("⚙️ RÉGLAGE SOLDE / REPORT", expanded=True):
        st.session_state.solde_ajustement = st.number_input("Ajustement / Report (€)", value=st.session_state.solde_ajustement)

    with st.expander("🏠 CHARGES FIXES", expanded=False):
        l_out = st.number_input("Loyer / Emprunt (€)", value=850)
        a_emp = st.number_input("Assurance Emprunt (€)", value=200)
        t_net = st.number_input("Tel + Internet (€)", value=90)
        e_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        kona = st.number_input("Kona + Assurance (€)", value=415)
        fam = st.number_input("Famille / Enfants (€)", value=200)
        a_vie = st.number_input("Assurance Vie (€)", value=50) # AJOUTÉ ICI
        
    with st.expander("📉 DÉCOUVERT & ÉPARGNE", expanded=True):
        remboursement = st.number_input("Remboursement ce mois (€)", value=995)
        obj_decouvert = st.number_input("Découvert total à combler (€)", value=2000)
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=False)
        mode_urgence = st.toggle("🚨 MODE VIGILANCE", value=False)

# --- CALCULS ---
now = datetime.now()
jours_mois = calendar.monthrange(now.year, now.month)[1]
rev_total = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie # Inclus Assurance Vie
epargne_auto = 1000 if active_agathe else 0

# Calcul du disponible mensuel après TOUTES les obligations
budget_dispo_mois = rev_total - charges_total - remboursement - epargne_auto
obj_journalier = budget_dispo_mois / jours_mois

# --- DASHBOARD ---
st.title(f"💎 Agathe Budget : {now.strftime('%B %Y')}")

df_h = load_data()
total_depense_mois = df_h["Montant"].sum()
aujourdhui = now.strftime("%Y-%m-%d")
depense_jour = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
reste_reel_jour = obj_journalier + st.session_state.solde_ajustement - depense_jour

c1, c2, c3 = st.columns(3)
c1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
c2.metric("DISPONIBLE RÉEL", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_ajustement:.2f} Reporté")
c3.metric("SOLDE PRÉVISIONNEL", f"{(budget_dispo_mois + st.session_state.solde_ajustement) - total_depense_mois:.2f} €")

st.divider()

# --- ANALYSE VISUELLE ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🧬 Évolution des Dépenses")
    if not df_h.empty:
        df_daily = df_h.groupby("Date")["Montant"].sum().reset_index()
        fig = px.area(df_daily, x="Date", y="Montant", color_discrete_sequence=["#00f2fe"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune dépense enregistrée pour le moment.")

with col_right:
    st.subheader("🎯 Suivi & Répartition")
    # Progression Découvert
    prog = min(1.0, (remboursement / (obj_decouvert if obj_decouvert > 0 else 1)))
    st.write(f"Découvert : {remboursement}€ / {obj_decouvert}€")
    st.progress(prog)
    
    if not df_h.empty:
        fig2 = px.pie(df_h, values='Montant', names='Type', hole=.5, color_discrete_sequence=px.colors.sequential.Teal)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- TABS ---
tab_saisie, tab_histo, tab_tresor, tab_admin = st.tabs(["✍️ SAISIE", "📑 HISTORIQUE", "💰 TRÉSOR", "⚙️ ARCHIVES"])

with tab_saisie:
    with st.form("form_saisie"):
        ca, cb, cc = st.columns([2,1,1])
        n = ca.text_input("Désignation")
        m = cb.number_input("Montant (€)", min_value=0.0, step=0.01)
        t = cc.selectbox("Catégorie", ["Vie Courante", "Courses", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 ENREGISTRER SUR LE CLOUD"):
            if n and m > 0:
                new_l = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": t, "Mode": "Urgence" if mode_urgence else "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_l], ignore_index=True))
                st.balloons()
                st.rerun()

with tab_histo:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer la Journée & Reporter le surplus"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with tab_tresor:
    st.subheader("💎 Trésor & Assurance")
    col1, col2 = st.columns(2)
    col1.metric("Épargne Agathe (1000€)", "ACTIVE" if active_agathe else "OFF")
    col2.metric("Assurance Vie Mensuelle", f"{a_vie} €")
    st.write("Ces montants sont automatiquement déduits de votre budget quotidien pour garantir la croissance de votre patrimoine.")

with tab_admin:
    st.subheader("🛡️ Gestion des Archives")
    if st.button("📦 SAUVEGARDER VERS ARCHIVES"):
        try:
            df_arch = load_data("Archives")
            df_final_arch = pd.concat([df_arch, df_h], ignore_index=True)
            conn.update(worksheet="Archives", data=df_final_arch)
            st.success("Sauvegarde terminée avec succès !")
        except:
            st.error("L'onglet 'Archives' est manquant dans Google Sheets.")

    if st.button("🗑️ RESET COMPLET DU MOIS"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.session_state.solde_ajustement = 0.0
        st.rerun()

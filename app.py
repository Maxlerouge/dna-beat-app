import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- CONFIGURATION ---
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

# --- SIDEBAR : PILOTAGE AGATHE ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("DNA-Beat v6.9 | Objectif 30€/J")
    
    with st.expander("💰 REVENUS", expanded=False):
        sal = st.number_input("Salaire Base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer Perçu (€)", value=588)
        h_sup = st.number_input("Heures Sup (€)", value=500)
        rev_extra = st.number_input("Revenu Supplémentaire (€)", value=0.0)
    
    with st.expander("⚙️ RÉGLAGE SOLDE DÉPART", expanded=True):
        st.session_state.solde_ajustement = st.number_input("Ajustement Solde (€)", value=st.session_state.solde_ajustement)

    with st.expander("🏠 CHARGES FIXES", expanded=False):
        l_out = st.number_input("Loyer / Emprunt (€)", value=850)
        a_emp = st.number_input("Assurance Emprunt (€)", value=200)
        t_net = st.number_input("Tel + Internet (€)", value=90)
        e_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        kona = st.number_input("Kona + Assurance (€)", value=415)
        fam = st.number_input("Famille / Enfants (€)", value=200)
        
    with st.expander("📉 DÉCOUVERT & ÉPARGNE", expanded=True):
        # MISE À JOUR : Valeur réglée à 995 € comme demandé
        decouvert_mensuel = st.number_input("Remboursement ce mois (€)", value=995)
        obj_decouvert_total = st.number_input("Découvert total à combler (€)", value=2000)
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=False)
        mode_urgence = st.toggle("🚨 MODE VIGILANCE", value=False)

# --- CALCULS ---
now = datetime.now()
jours_mois = calendar.monthrange(now.year, now.month)[1]
rev_total = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam
epargne_auto = 1000 if active_agathe else 0
coeff_urg = 0.7 if mode_urgence else 1.0

# Budget journalier recalibré
# On retire les charges, le remboursement et l'épargne. Le budget courses est inclus dans le reste à vivre.
budget_dispo_mois = rev_total - charges_total - decouvert_mensuel - epargne_auto
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
c2.metric("DISPONIBLE RÉEL", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_ajustement:.2f} Ajusté")
c3.metric("PROJECTION FIN MOIS", f"{(budget_dispo_mois + st.session_state.solde_ajustement) - total_depense_mois:.2f} €")

st.divider()

# --- TABS ---
tab_saisie, tab_histo, tab_admin = st.tabs(["✍️ SAISIE", "📑 HISTORIQUE", "⚙️ ARCHIVES"])

with tab_saisie:
    with st.form("form_saisie"):
        ca, cb, cc = st.columns([2,1,1])
        n = ca.text_input("Désignation")
        m = cb.number_input("Montant (€)", min_value=0.0, step=0.01)
        t = cc.selectbox("Catégorie", ["Vie Courante", "Courses", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 ENREGISTRER"):
            if n and m > 0:
                new_l = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": t, "Mode": "Urgence" if mode_urgence else "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_l], ignore_index=True))
                st.balloons()
                st.rerun()

with tab_histo:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer Journée (Report vers Ajustement)"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with tab_admin:
    st.subheader("🛡️ Gestion des Archives")
    st.info("Rappel : Créez l'onglet 'Archives' dans votre Google Sheet pour activer cette fonction.")
    
    if st.button("📦 LANCER LA SAUVEGARDE VERS ARCHIVES"):
        try:
            df_arch = load_data("Archives")
            df_final_arch = pd.concat([df_arch, df_h], ignore_index=True)
            conn.update(worksheet="Archives", data=df_final_arch)
            st.success("Synchronisation réussie !")
        except:
            st.error("Onglet 'Archives' introuvable dans le Google Sheet.")

    if st.button("🗑️ REMISE À ZÉRO DU MOIS"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.session_state.solde_ajustement = 0.0
        st.rerun()

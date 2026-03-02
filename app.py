import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- CONFIGURATION ---
st.set_page_config(page_title="Agathe Budget | DNA-Beat", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e); color: #e0e0e0; }
    [data-testid="stMetric"] { background: rgba(0, 242, 254, 0.05); border-left: 5px solid #00f2fe; border-radius: 10px; padding: 15px; }
    .stButton>button { width: 100%; border-radius: 20px; border: 1px solid #00f2fe; background: transparent; color: #00f2fe; font-weight: bold; }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 8px rgba(0, 242, 254, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SYSTÈME DE MÉMOIRE CLOUD ---
def load_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        return dict(zip(df_conf['Variable'], df_conf['Valeur']))
    except:
        return {}

def save_config(d):
    df_save = pd.DataFrame(list(d.items()), columns=['Variable', 'Valeur'])
    conn.update(worksheet="Config", data=df_save)

conf_cloud = load_config()

# --- SIDEBAR : VÉRIFICATION DE TOUTES LES VARIABLES ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("DNA-Beat v7.8 | 2026")
    
    with st.expander("💰 REVENUS", expanded=False):
        sal = st.number_input("Salaire Base", value=float(conf_cloud.get("sal", 3500.0)))
        caaf = st.number_input("CAAF", value=float(conf_cloud.get("caaf", 150.0)))
        loyer_in = st.number_input("Loyer Perçu", value=float(conf_cloud.get("loyer_in", 588.0)))
        h_sup = st.number_input("Heures Sup", value=float(conf_cloud.get("h_sup", 500.0)))
        rev_extra = st.number_input("Revenu Extra", value=float(conf_cloud.get("rev_extra", 0.0)))
    
    # Report de solde (Mémoire Session)
    if 'solde_ajustement' not in st.session_state:
        st.session_state.solde_ajustement = float(conf_cloud.get("last_report", 0.0))
    st.session_state.solde_ajustement = st.number_input("Ajustement / Report (€)", value=st.session_state.solde_ajustement)

    with st.expander("🏠 CHARGES FIXES", expanded=False):
        l_out = st.number_input("Loyer / Emprunt", value=float(conf_cloud.get("l_out", 850.0)))
        a_emp = st.number_input("Assurance Emprunt", value=float(conf_cloud.get("a_emp", 200.0)))
        t_net = st.number_input("Tel + Internet", value=float(conf_cloud.get("t_net", 90.0)))
        e_eau = st.number_input("EDF + Eau", value=float(conf_cloud.get("e_eau", 298.0)))
        mgen = st.number_input("MGEN", value=float(conf_cloud.get("mgen", 160.0)))
        kona = st.number_input("Kona + Assurance", value=float(conf_cloud.get("kona", 415.0)))
        fam = st.number_input("Famille / Enfants", value=float(conf_cloud.get("fam", 200.0)))
        a_vie = st.number_input("Assurance Vie", value=float(conf_cloud.get("a_vie", 50.0)))
        # La variable "Divers" est officiellement absente.

    with st.expander("📉 DÉCOUVERT & STRATÉGIE", expanded=True):
        remboursement = st.number_input("Remboursement ce mois", value=float(conf_cloud.get("remboursement", 600.0)))
        obj_decouvert = st.number_input("Découvert Total Cible", value=float(conf_cloud.get("obj_decouvert", 2000.0)))
        budget_bouffe = st.slider("Budget Courses / Bouffe (€)", 300, 1000, int(conf_cloud.get("budget_bouffe", 600)))
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=conf_cloud.get("active_agathe", 0) == 1)
        mode_urgence = st.toggle("🚨 MODE VIGILANCE", value=conf_cloud.get("mode_urgence", 0) == 1)

    if st.button("💾 SAUVEGARDER TOUTE LA CONFIGURATION"):
        config_a_sauver = {
            "sal": sal, "caaf": caaf, "loyer_in": loyer_in, "h_sup": h_sup, "rev_extra": rev_extra,
            "l_out": l_out, "a_emp": a_emp, "t_net": t_net, "e_eau": e_eau, "mgen": mgen,
            "kona": kona, "fam": fam, "a_vie": a_vie, "remboursement": remboursement,
            "obj_decouvert": obj_decouvert, "budget_bouffe": budget_bouffe,
            "active_agathe": 1 if active_agathe else 0, "mode_urgence": 1 if mode_urgence else 0,
            "last_report": st.session_state.solde_ajustement
        }
        save_config(config_a_sauver)
        st.success("Toutes les variables sont enregistrées dans Config !")

# --- CALCULS PRÉCIS ---
now = datetime.now()
jours_mois = calendar.monthrange(now.year, now.month)[1]

# 1. Total Revenus
rev_total = sal + caaf + loyer_in + h_sup + rev_extra

# 2. Total Charges (VÉRIFIÉ : Pas de variable 'Divers' oubliée)
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie

# 3. Stratégie
epargne_auto = 1000 if active_agathe else 0
coeff_urg = 0.7 if mode_urgence else 1.0

# 4. Disponible final
budget_dispo_mensuel = rev_total - charges_total - remboursement - epargne_auto - (budget_bouffe * coeff_urg)
obj_journalier = budget_dispo_mensuel / jours_mois

# --- DASHBOARD & GRAPHIQUES ---
st.title(f"💎 Dashboard Agathe : {now.strftime('%B %Y')}")
df_h = conn.read(worksheet="Historique", ttl=0)
if df_h is None or df_h.empty:
    df_h = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

total_depense_mois = pd.to_numeric(df_h["Montant"]).sum()
reste_reel_jour = obj_journalier + st.session_state.solde_ajustement - df_h[df_h["Date"] == now.strftime("%Y-%m-%d")]["Montant"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
c2.metric("LIBERTÉ RÉELLE JOUR", f"{reste_reel_jour:.2f} €")
c3.metric("RESTANT FIN MOIS", f"{(budget_dispo_mensuel + st.session_state.solde_ajustement) - total_depense_mois:.2f} €")

st.divider()

# --- ONGLETS ---
t1, t2, t3 = st.tabs(["✍️ SAISIE", "📑 HISTORIQUE", "⚙️ GESTION"])

with t1:
    with st.form("ajout"):
        ca, cb, cc = st.columns([2,1,1])
        n = ca.text_input("Désignation")
        m = cb.number_input("Montant (€)", min_value=0.0)
        cat = cc.selectbox("Catégorie", ["Courses", "Vie Courante", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 VALIDER L'ACHAT"):
            new_row = pd.DataFrame([{"Date": now.strftime("%Y-%m-%d"), "Nom": n, "Montant": m, "Type": cat, "Mode": "Normal"}])
            conn.update(worksheet="Historique", data=pd.concat([df_h, new_row], ignore_index=True))
            st.rerun()

with t2:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer Journée (Report automatique)"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with t3:
    st.subheader("📦 Archives")
    if st.button("SAUVEGARDER LE MOIS DANS ARCHIVES"):
        try:
            df_arch = conn.read(worksheet="Archives", ttl=0)
            conn.update(worksheet="Archives", data=pd.concat([df_arch, df_h], ignore_index=True))
            st.success("Archivage OK")
        except: st.error("Onglet 'Archives' manquant !")

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
    .stProgress > div > div > div > div { background-color: #00f2fe; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION CLOUD ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        return dict(zip(df_conf['Variable'], df_conf['Valeur']))
    except: return {}

def save_config(d):
    df_save = pd.DataFrame(list(d.items()), columns=['Variable', 'Valeur'])
    conn.update(worksheet="Config", data=df_save)

conf_cloud = load_config()

# --- SIDEBAR (100% DES VARIABLES RÉINTÉGRÉES) ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    
    with st.expander("💰 REVENUS", expanded=False):
        sal = st.number_input("Salaire Base", value=float(conf_cloud.get("sal", 3500.0)))
        caaf = st.number_input("CAAF", value=float(conf_cloud.get("caaf", 150.0)))
        loyer_in = st.number_input("Loyer Perçu", value=float(conf_cloud.get("loyer_in", 588.0)))
        h_sup = st.number_input("Heures Sup", value=float(conf_cloud.get("h_sup", 500.0)))
        rev_extra = st.number_input("Revenu Extra", value=float(conf_cloud.get("rev_extra", 0.0)))
    
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
        fam = st.number_input("Famille", value=float(conf_cloud.get("fam", 200.0)))
        a_vie = st.number_input("Assurance Vie", value=float(conf_cloud.get("a_vie", 50.0)))

    with st.expander("📉 DÉCOUVERT & STRATÉGIE", expanded=True):
        remboursement = st.number_input("Remboursement ce mois", value=float(conf_cloud.get("remboursement", 600.0)))
        obj_decouvert = st.number_input("Découvert Total Cible", value=float(conf_cloud.get("obj_decouvert", 2000.0)))
        budget_bouffe = st.slider("Budget Courses (€)", 300, 1000, int(conf_cloud.get("budget_bouffe", 600)))
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=conf_cloud.get("active_agathe", 0) == 1)
        mode_urgence = st.toggle("🚨 MODE VIGILANCE", value=conf_cloud.get("mode_urgence", 0) == 1)

    if st.button("💾 SAUVEGARDER CONFIGURATION"):
        save_config({
            "sal": sal, "caaf": caaf, "loyer_in": loyer_in, "h_sup": h_sup, "rev_extra": rev_extra,
            "l_out": l_out, "a_emp": a_emp, "t_net": t_net, "e_eau": e_eau, "mgen": mgen,
            "kona": kona, "fam": fam, "a_vie": a_vie, "remboursement": remboursement,
            "obj_decouvert": obj_decouvert, "budget_bouffe": budget_bouffe,
            "active_agathe": 1 if active_agathe else 0, "mode_urgence": 1 if mode_urgence else 0,
            "last_report": st.session_state.solde_ajustement
        })
        st.success("Config Cloud Mise à jour !")

# --- MOTEUR DE CALCUL (SÉCURITÉ MAX) ---
now = datetime.today()
jours_dans_mois = calendar.monthrange(now.year, now.month)[1]

df_raw = conn.read(worksheet="Historique", ttl=0)

# On prépare un dataframe propre même si le Sheets est vide
if df_raw is None or df_raw.empty:
    df_h = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
    df_mois = df_h.copy()
else:
    df_h = df_raw.copy()
    # CONVERSION CRITIQUE : on force le format et on vire ce qui n'est pas une date
    df_h["Date"] = pd.to_datetime(df_h["Date"], errors='coerce')
    df_h = df_h.dropna(subset=["Date"])
    df_h["Montant"] = pd.to_numeric(df_h["Montant"], errors='coerce').fillna(0)
    
    # FILTRAGE SANS RISQUE
    df_mois = df_h[(df_h["Date"].dt.month == now.month) & (df_h["Date"].dt.year == now.year)].copy()

# Calculs Budget
rev_total = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie
epargne_agathe = 1000 if active_agathe else 0
coeff_urg = 0.7 if mode_urgence else 1.0

budget_mois_dispo = rev_total - charges_total - remboursement - epargne_agathe - (budget_bouffe * coeff_urg)
obj_journalier = budget_mois_dispo / jours_dans_mois

# Calculs Dépenses
total_depenses_mois = df_mois["Montant"].sum()
# Comparaison de dates simplifiée pour éviter l'erreur .dt
today_str = now.strftime('%Y-%m-%d')
depense_aujourdhui = df_mois[df_mois["Date"].dt.strftime('%Y-%m-%d') == today_str]["Montant"].sum()
reste_reel_jour = obj_journalier + st.session_state.solde_ajustement - depense_aujourdhui

# --- INTERFACE ---
st.title(f"💎 Agathe Budget : {now.strftime('%B %Y')}")

# JAUGE DÉCOUVERT
st.subheader("🎯 Progression du Remboursement")
prog = min(1.0, remboursement / obj_decouvert)
st.progress(prog)
st.caption(f"{remboursement}€ payés sur {obj_decouvert}€ ({int(prog*100)}%)")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
col2.metric("DISPO RÉEL JOUR", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_ajustement:.2f}")
col3.metric("SOLDE FIN MOIS", f"{(budget_mois_dispo + st.session_state.solde_ajustement) - total_depenses_mois:.2f} €")

st.divider()

# --- GRAPHIQUES ---
ga, gb = st.columns([2, 1])
with ga:
    st.subheader("🧬 Évolution Dépenses")
    if not df_mois.empty:
        df_p = df_mois.groupby(df_mois["Date"].dt.date)["Montant"].sum().reset_index()
        fig = px.area(df_p, x="Date", y="Montant", color_discrete_sequence=["#00f2fe"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

with gb:
    st.subheader("📊 Répartition")
    if not df_mois.empty:
        fig2 = px.pie(df_mois, values='Montant', names='Type', hole=.5, color_discrete_sequence=px.colors.sequential.Teal)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- TABS ---
t1, t2, t3 = st.tabs(["✍️ SAISIE", "📑 HISTORIQUE", "⚙️ ARCHIVES"])
with t1:
    with st.form("add"):
        c_a, c_b, c_c = st.columns([2,1,1])
        n = c_a.text_input("Désignation")
        m = c_b.number_input("Montant", min_value=0.0)
        t = c_c.selectbox("Catégorie", ["Courses", "Vie Courante", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("VALIDER"):
            new_row = pd.DataFrame([{"Date": now.strftime("%Y-%m-%d"), "Nom": n, "Montant": m, "Type": t, "Mode": "Normal"}])
            conn.update(worksheet="Historique", data=pd.concat([df_h, new_row], ignore_index=True))
            st.rerun()

with t2:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer Journée"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with t3:
    if st.button("📦 ARCHIVER"):
        try:
            df_arch = conn.read(worksheet="Archives", ttl=0)
            conn.update(worksheet="Archives", data=pd.concat([df_arch, df_h], ignore_index=True))
            st.success("Archivage OK")
        except: st.error("Onglet Archives ?")

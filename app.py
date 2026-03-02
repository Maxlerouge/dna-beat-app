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

# --- CONNEXION & MÉMOIRE ---
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

# --- SIDEBAR : TOUTES TES VARIABLES ---
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
        st.success("Config Cloud Mémorisée !")

# --- CALCULS ---
now = datetime.now()
jours_mois = calendar.monthrange(now.year, now.month)[1]
rev_total = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie
epargne_agathe = 1000 if active_agathe else 0
coeff_urg = 0.7 if mode_urgence else 1.0
budget_mois = rev_total - charges_total - remboursement - epargne_agathe - (budget_bouffe * coeff_urg)
obj_journalier = budget_mois / jours_mois

# --- DASHBOARD ---
st.title(f"💎 Agathe Budget : {now.strftime('%B %Y')}")

# JAUGE DÉCOUVERT
st.subheader("🎯 Suivi du Découvert")
progression = min(1.0, remboursement / obj_decouvert)
st.progress(progression)
st.caption(f"Objectif : {obj_decouvert}€ | Remboursé ce mois : {remboursement}€ ({int(progression*100)}%)")

st.divider()

# MÉTRIQUES
df_h = conn.read(worksheet="Historique", ttl=0)
if df_h is None or df_h.empty: df_h = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
df_h["Montant"] = pd.to_numeric(df_h["Montant"], errors='coerce').fillna(0)

total_dep_mois = df_h["Montant"].sum()
dep_jour = df_h[df_h["Date"] == now.strftime("%Y-%m-%d")]["Montant"].sum()
reste_reel_jour = obj_journalier + st.session_state.solde_ajustement - dep_jour

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
col_m2.metric("DISPONIBLE DU JOUR", f"{reste_reel_jour:.2f} €", delta=f"{st.session_state.solde_ajustement:.2f} Reporté")
col_m3.metric("SOLDE FIN MOIS", f"{(budget_mois + st.session_state.solde_ajustement) - total_dep_mois:.2f} €")

st.divider()

# --- GRAPHIQUES (RÉINTÉGRÉS) ---
col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    st.subheader("🧬 Évolution des Dépenses")
    if not df_h.empty:
        df_daily = df_h.groupby("Date")["Montant"].sum().reset_index()
        fig = px.area(df_daily, x="Date", y="Montant", color_discrete_sequence=["#00f2fe"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", 
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée pour le graphique d'évolution.")

with col_g2:
    st.subheader("📊 Répartition par Type")
    if not df_h.empty:
        fig2 = px.pie(df_h, values='Montant', names='Type', hole=.6, 
                      color_discrete_sequence=px.colors.sequential.Teal_r)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- ACTIONS & HISTORIQUE ---
tab1, tab2, tab3 = st.tabs(["✍️ NOUVEL ACHAT", "📑 HISTORIQUE COMPLET", "⚙️ ARCHIVES"])

with tab1:
    with st.form("ajout_achat"):
        c_a, c_b, c_c = st.columns([2,1,1])
        nom = c_a.text_input("Désignation")
        montant = c_b.number_input("Montant (€)", min_value=0.0, step=0.01)
        categorie = c_c.selectbox("Catégorie", ["Courses", "Vie Courante", "Loisirs", "Santé", "Imprévu"])
        if st.form_submit_button("🔨 ENREGISTRER"):
            if nom and montant > 0:
                new_line = pd.DataFrame([{"Date": now.strftime("%Y-%m-%d"), "Nom": nom, "Montant": montant, "Type": categorie, "Mode": "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_line], ignore_index=True))
                st.rerun()

with tab2:
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    if st.button("🌙 Clôturer la Journée & Reporter le surplus"):
        st.session_state.solde_ajustement = reste_reel_jour
        st.rerun()

with tab3:
    if st.button("📦 ARCHIVER LE MOIS"):
        try:
            df_arch = conn.read(worksheet="Archives", ttl=0)
            conn.update(worksheet="Archives", data=pd.concat([df_arch, df_h], ignore_index=True))
            st.success("Données envoyées vers l'onglet Archives.")
        except: st.error("L'onglet 'Archives' est introuvable.")

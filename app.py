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

# --- FONCTIONS DE LECTURE/ÉCRITURE ---
def get_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        return dict(zip(df_conf['Variable'], df_conf['Valeur']))
    except:
        # Valeurs par défaut si l'onglet Config est vide/inexistant
        return {
            "sal": 3500.0, "caaf": 150.0, "loyer_in": 588.0, "h_sup": 500.0,
            "l_out": 850.0, "a_emp": 200.0, "t_net": 90.0, "e_eau": 298.0,
            "mgen": 160.0, "kona": 415.0, "fam": 200.0, "a_vie": 50.0,
            "remboursement": 600.0, "budget_bouffe": 600.0
        }

def save_config(config_dict):
    df_save = pd.DataFrame(list(config_dict.items()), columns=['Variable', 'Valeur'])
    conn.update(worksheet="Config", data=df_save)

def load_histo():
    try:
        df = conn.read(worksheet="Historique", ttl=0)
        return df if df is not None else pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])

# --- CHARGEMENT INITIAL ---
conf = get_config()
if 'solde_ajustement' not in st.session_state: st.session_state.solde_ajustement = 0.0

# --- SIDEBAR (MODIFICATIONS SAUVEGARDÉES) ---
with st.sidebar:
    st.title("💎 AGATHE BUDGET")
    st.caption("v7.6 | Mémoire Cloud Active")
    
    with st.expander("💰 REVENUS", expanded=False):
        c_sal = st.number_input("Salaire Base", value=float(conf.get("sal", 3500)))
        c_caaf = st.number_input("CAAF", value=float(conf.get("caaf", 150)))
        c_loyer_in = st.number_input("Loyer Perçu", value=float(conf.get("loyer_in", 588)))
        c_h_sup = st.number_input("Heures Sup", value=float(conf.get("h_sup", 500)))

    with st.expander("🏠 CHARGES FIXES", expanded=False):
        c_lout = st.number_input("Loyer/Prêt", value=float(conf.get("l_out", 850)))
        c_aemp = st.number_input("Assurance Emprunt", value=float(conf.get("a_emp", 200)))
        c_eau = st.number_input("EDF/Eau", value=float(conf.get("e_eau", 298)))
        c_avie = st.number_input("Assurance Vie", value=float(conf.get("a_vie", 50)))
        # ... (ajoute les autres au besoin sur le même modèle)

    with st.expander("📉 STRATÉGIE", expanded=True):
        c_remb = st.number_input("Remboursement", value=float(conf.get("remboursement", 600)))
        c_bouffe = st.slider("Budget Courses", 300, 1000, int(conf.get("budget_bouffe", 600)))
        active_agathe = st.toggle("Activer Trésor Agathe (1000€)", value=False)

    if st.button("💾 SAUVEGARDER LES RÉGLAGES"):
        new_conf = {
            "sal": c_sal, "caaf": c_caaf, "loyer_in": c_loyer_in, "h_sup": c_h_sup,
            "l_out": c_lout, "a_emp": c_aemp, "e_eau": c_eau, "a_vie": c_avie,
            "remboursement": c_remb, "budget_bouffe": c_bouffe
        }
        save_config(new_conf)
        st.success("Réglages mémorisés dans le Cloud !")

# --- CALCULS ---
rev_total = c_sal + c_caaf + c_loyer_in + c_h_sup
# Note : Charges simplifiées ici pour l'exemple, garde toutes tes variables dans ton code complet
charges_total = c_lout + c_aemp + c_eau + c_avie + 160 + 415 + 200 + 90 
epargne_agathe = 1000 if active_agathe else 0
jours_mois = calendar.monthrange(datetime.now().year, datetime.now().month)[1]

budget_mois = rev_total - charges_total - c_remb - epargne_agathe - c_bouffe
obj_journalier = budget_mois / jours_mois

# --- DASHBOARD ---
st.title(f"💎 Pilotage : {datetime.now().strftime('%B %Y')}")
df_h = load_histo()
reste_jour = obj_journalier + st.session_state.solde_ajustement - df_h[df_h["Date"] == datetime.now().strftime("%Y-%m-%d")]["Montant"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("OBJECTIF / JOUR", f"{obj_journalier:.2f} €")
c2.metric("DISPONIBLE RÉEL", f"{reste_jour:.2f} €")
c3.metric("PRÉVISION FIN MOIS", f"{(budget_mois + st.session_state.solde_ajustement) - df_h['Montant'].sum():.2f} €")

# --- GRAPHIQUE ---
if not df_h.empty:
    fig = px.area(df_h.groupby("Date")["Montant"].sum().reset_index(), x="Date", y="Montant", color_discrete_sequence=["#00f2fe"])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- ACTIONS ---
t1, t2, t3 = st.tabs(["✍️ SAISIE", "📑 HISTORIQUE", "⚙️ ARCHIVES"])
# ... (garde tes formulaires de saisie et d'archivage ici)

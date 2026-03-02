import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import calendar

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Agathe Budget", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 25px; border: 1px solid #00f2fe;
        background: transparent; color: #00f2fe;
    }
    h1, h2, h3 { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
# Note : Tu dois configurer l'URL dans les secrets de Streamlit (st.secrets["connections"]["gsheets"]["url"])
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        return conn.read(worksheet="Historique", ttl=0)
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Montant", "Type"])

# --- INITIALISATION ÉTAT (SESSION) ---
if 'solde_reporte' not in st.session_state:
    st.session_state.solde_reporte = 0.0
if 'tresor_agathe' not in st.session_state:
    st.session_state.tresor_agathe = 0.0

# --- SIDEBAR : VARIABLES MODIFIABLES ---
with st.sidebar:
    st.title("🛸 NAVIGATION")
    
    with st.expander("💰 REVENUS", expanded=False):
        sal = st.number_input("Salaire base (€)", value=3500)
        caaf = st.number_input("CAAF (€)", value=150)
        loyer_in = st.number_input("Loyer perçu (€)", value=588)
        h_sup = st.slider("Heures Sup' (€)", 0, 1500, 500)
    
    with st.expander("🏠 CHARGES", expanded=False):
        loyer_out = st.number_input("Loyer emprunt (€)", value=850)
        assu_emp = st.number_input("Assurance emprunt (€)", value=200)
        tel_net = st.number_input("Tel + Internet (€)", value=90)
        edf_eau = st.number_input("EDF + Eau (€)", value=298)
        mgen = st.number_input("MGEN (€)", value=160)
        voiture = st.number_input("Kona + Assu (€)", value=415)
        famille = st.number_input("Enfants (€)", value=200)
        divers = st.number_input("Autres (€)", value=110)

    with st.expander("🎯 STRATÉGIE", expanded=True):
        remboursement = st.number_input("Remboursement Découvert (€)", value=600)
        courses_max = st.slider("Budget Courses (€)", 300, 900, 600)
        active_agathe = st.toggle("Activer Agathe Budget", value=False)

# --- CALCULS ---
now = datetime.now()
jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
total_rev = sal + caaf + loyer_in + h_sup
total_charges = loyer_out + assu_emp + tel_net + edf_eau + mgen + voiture + famille + divers
epargne_mensuelle = 1000 if active_agathe else 0
reste_mensuel = total_rev - total_charges - courses_max - remboursement - epargne_mensuelle
budget_jour_base = reste_mensuel / jours_dans_le_mois

# --- INTERFACE ---
st.title("🧬 Agathe Budget : Pilotage Odyssée")

tab1, tab2, tab3 = st.tabs(["⚡ DASHBOARD", "📑 HISTORIQUE", "💎 TRÉSOR"])

with tab1:
    df_historique = get_data()
    aujourdhui = now.strftime("%Y-%m-%d")
    depenses_today = df_historique[df_historique["Date"] == aujourdhui]["Montant"].sum()
    dispo_aujourdhui = budget_jour_base + st.session_state.solde_reporte - depenses_today
    
    col1, col2 = st.columns(2)
    col1.metric("OBJECTIF JOUR", f"{budget_jour_base:.2f} €")
    col2.metric("RESTE RÉEL", f"{dispo_aujourdhui:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} Report")
    
    st.divider()
    if st.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = dispo_aujourdhui
        if active_agathe: st.session_state.tresor_agathe += (1000 / jours_dans_le_mois)
        st.success("Journée clôturée !")
    
    if st.button("🔄 Reset Report Journée"):
        st.session_state.solde_reporte = 0.0
        st.rerun()

with tab2:
    st.subheader("Saisie d'achat")
    with st.form("form_saisie"):
        n = st.text_input("Désignation")
        m = st.number_input("Montant (€)", min_value=0.0)
        t = st.selectbox("Catégorie", ["Vie", "Fixe", "Loisir"])
        if st.form_submit_button("🔨 Envoyer vers Google Sheets"):
            if n and m > 0:
                new_entry = pd.DataFrame([{"Date": aujourdhui, "Nom": n, "Montant": m, "Type": t}])
                updated_df = pd.concat([df_historique, new_entry], ignore_index=True)
                conn.update(worksheet="Historique", data=updated_df)
                st.success("Données sauvegardées à vie !")
                st.rerun()
            
    st.dataframe(df_historique.sort_values(by="Date", ascending=False), use_container_width=True)
    
    if st.button("🗑️ Reset Historique (Attention : Efface Google Sheets)"):
        empty_df = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type"])
        conn.update(worksheet="Historique", data=empty_df)
        st.rerun()

with tab3:
    st.subheader("Capital Agathe Budget")
    st.metric("Trésor Accumulé", f"{st.session_state.tresor_agathe:.2f} €")
    st.progress(min(1.0, st.session_state.tresor_agathe / 10000))
    
    if st.button("🏁 Reset Trésor"):
        st.session_state.tresor_agathe = 0.0
        st.rerun()

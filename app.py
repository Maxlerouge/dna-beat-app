import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import calendar
import plotly.express as px # Pour les graphiques pro

# --- DESIGN DNA-BEAT ---
st.set_page_config(page_title="Agathe Budget - DNA-Beat", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    [data-testid="stMetric"] { background: rgba(0, 242, 254, 0.05); border-left: 5px solid #00f2fe; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.05); border-radius: 10px 10px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION ---
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
if 'tresor_agathe' not in st.session_state: st.session_state.tresor_agathe = 0.0

# --- SIDEBAR DYNAMIQUE ---
with st.sidebar:
    st.title("🧬 DNA-BEAT")
    mode_urgence = st.toggle("🚨 MODE VIGILANCE RAPPROCHÉE", value=False)
    
    with st.expander("💰 REVENUS (Instituteur d'État)", expanded=False):
        total_rev = st.number_input("Salaire + IRL + CAAF + Loyer In", value=4538)
        h_sup = st.number_input("Heures Sup du mois", value=500)
    
    with st.expander("🏠 CHARGES FIXES", expanded=False):
        fixes = st.number_input("Total Charges (Loyer/MGEN/Kona/Famille)", value=2328)
        remboursement = st.number_input("Remboursement Découvert", value=600)
        
    with st.expander("🎯 STRATÉGIE", expanded=True):
        courses_max = st.slider("Budget Courses", 300, 900, 600)
        active_agathe = st.toggle("Épargne Agathe (1000€)", value=False)

# --- CALCULS ---
now = datetime.now()
jours_restants = calendar.monthrange(now.year, now.month)[1] - now.day + 1
revenu_total = total_rev + h_sup
epargne_cible = 1000 if active_agathe else 0
budget_total_dispo = revenu_total - fixes - remboursement - epargne_cible - (courses_max * (0.7 if mode_urgence else 1.0))
budget_journalier = budget_total_dispo / calendar.monthrange(now.year, now.month)[1]

# --- INTERFACE ---
st.title(f"🚀 DNA-Beat : Pilotage de Mars 2026") # Dynamique avec l'année actuelle

tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "📝 SAISIE", "📑 ANALYSE"])

df_h = load_data()

with tab1:
    # Calculs temps réel
    aujourdhui = now.strftime("%Y-%m-%d")
    depenses_jour = df_h[df_h["Date"] == aujourdhui]["Montant"].sum()
    reste_du_jour = budget_journalier + st.session_state.solde_reporte - depenses_jour
    
    c1, c2, c3 = st.columns(3)
    c1.metric("OBJECTIF / JOUR", f"{budget_journalier:.2f} €")
    c2.metric("RESTE POUR AUJOURD'HUI", f"{reste_du_jour:.2f} €", delta=f"{st.session_state.solde_reporte:.2f} Reporté")
    
    # Projection fin de mois
    total_depense_mois = df_h["Montant"].sum()
    projection_fin_mois = budget_total_dispo - total_depense_mois
    c3.metric("PROJECTION FIN DE MOIS", f"{projection_fin_mois:.2f} €", delta_color="normal")

    st.divider()
    
    # Graphique de répartition
    if not df_h.empty:
        fig = px.pie(df_h, values='Montant', names='Type', hole=.4, 
                     title="Répartition des dépenses",
                     color_discrete_sequence=px.colors.sequential.Cyan)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.form("ajout_rapide"):
        col1, col2, col3 = st.columns([2,1,1])
        nom = col1.text_input("Désignation", placeholder="Ex: Boulangerie, Essence...")
        mt = col2.number_input("Montant (€)", min_value=0.0, step=0.5)
        cat = col3.selectbox("Catégorie", ["Vie Courante", "Courses", "Loisirs", "Imprévu", "Santé"])
        
        if st.form_submit_button("🔨 ENREGISTRER L'OPÉRATION"):
            if nom and mt > 0:
                new_row = pd.DataFrame([{"Date": aujourdhui, "Nom": nom, "Montant": mt, "Type": cat, "Mode": "Urgence" if mode_urgence else "Normal"}])
                conn.update(worksheet="Historique", data=pd.concat([df_h, new_row], ignore_index=True))
                st.balloons()
                st.rerun()

    st.info(f"💡 Il reste {jours_restants} jours dans le mois. Tenez bon !")

with tab3:
    st.subheader("Historique Complet")
    st.dataframe(df_h.sort_values(by="Date", ascending=False), use_container_width=True)
    
    c_a, c_b, c_c = st.columns(3)
    if c_a.button("🌙 Clôturer la journée"):
        st.session_state.solde_reporte = reste_du_jour
        st.rerun()
    if c_b.button("🔄 Reset Report"):
        st.session_state.solde_reporte = 0.0
        st.rerun()
    if c_c.button("🗑️ Vider l'historique"):
        conn.update(worksheet="Historique", data=pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"]))
        st.rerun()

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import calendar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# CONFIG PAGE
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="💸 Agathe Budget",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════
# THEME COLORÉ & FUN
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --pink:    #FF6B9D;
    --orange:  #FF9F43;
    --yellow:  #FECA57;
    --green:   #1DD1A1;
    --blue:    #54A0FF;
    --purple:  #A29BFE;
    --bg:      #1E1B2E;
    --surface: #2A2740;
    --surface2:#332F50;
    --text:    #F0EEF8;
    --muted:   #9E9BBF;
}

* { font-family: 'Nunito', sans-serif; }

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(255,107,157,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(84,160,255,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(162,155,254,0.05) 0%, transparent 70%);
    color: var(--text);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 2px solid var(--surface2);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* HEADERS */
h1 { font-family: 'Fredoka One', cursive !important; font-size: 2.5rem !important; 
     background: linear-gradient(90deg, var(--pink), var(--orange), var(--yellow));
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
h2 { font-family: 'Fredoka One', cursive !important; color: var(--purple) !important; font-size: 1.6rem !important; }
h3 { color: var(--blue) !important; font-weight: 800 !important; }

/* METRICS */
[data-testid="stMetric"] {
    background: var(--surface);
    border-radius: 16px;
    padding: 20px !important;
    border-top: 4px solid var(--pink);
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-3px); }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-weight: 700 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Fredoka One', cursive !important; font-size: 2rem !important; }
[data-testid="stMetricDelta"] { font-weight: 700 !important; }

/* CARDS */
.budget-card {
    background: var(--surface);
    border-radius: 20px;
    padding: 24px;
    margin: 8px 0;
    border: 1px solid var(--surface2);
}
.emoji-badge {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 8px;
}
.stat-label {
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}
.stat-value {
    color: var(--text);
    font-family: 'Fredoka One', cursive;
    font-size: 1.8rem;
    margin: 4px 0;
}

/* PROGRESS BAR CUSTOM */
.progress-wrap {
    background: var(--surface2);
    border-radius: 999px;
    height: 16px;
    overflow: hidden;
    margin: 8px 0;
}
.progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s cubic-bezier(.34,1.56,.64,1);
}

/* BOUTONS */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important; }

/* TABS */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--surface);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--pink), var(--purple)) !important;
    color: white !important;
}

/* INPUTS */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: var(--surface2) !important;
    border: 1px solid var(--surface2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--pink) !important;
    box-shadow: 0 0 0 3px rgba(255,107,157,0.2) !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--surface2);
}

/* ALERT / WARNING */
.fun-alert {
    background: linear-gradient(135deg, rgba(255,159,67,0.15), rgba(254,202,87,0.15));
    border: 1px solid var(--orange);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}
.fun-alert-danger {
    background: linear-gradient(135deg, rgba(255,107,107,0.15), rgba(255,107,157,0.15));
    border: 1px solid var(--pink);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}
.fun-alert-success {
    background: linear-gradient(135deg, rgba(29,209,161,0.15), rgba(84,160,255,0.15));
    border: 1px solid var(--green);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* DIVIDER */
.rainbow-divider {
    height: 3px;
    background: linear-gradient(90deg, var(--pink), var(--orange), var(--yellow), var(--green), var(--blue), var(--purple));
    border-radius: 999px;
    margin: 24px 0;
}

/* EXPANDER */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--surface2) !important;
    border-radius: 12px !important;
}

/* SUCCESS/ERROR messages */
.stSuccess { background: rgba(29,209,161,0.15) !important; border-color: var(--green) !important; }
.stError   { background: rgba(255,107,157,0.15) !important; border-color: var(--pink) !important; }
.stWarning { background: rgba(255,159,67,0.15) !important; border-color: var(--orange) !important; }

/* SLIDER */
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] { color: var(--yellow) !important; }

/* TOGGLE */
.stToggle { color: var(--text) !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--purple); border-radius: 999px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# CONNEXION GOOGLE SHEETS
# ═══════════════════════════════════════════════
@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

# ═══════════════════════════════════════════════
# FONCTIONS CLOUD — ROBUSTES
# ═══════════════════════════════════════════════
def load_config() -> dict:
    """Charge la config depuis GSheets avec valeurs par défaut."""
    defaults = {
        "sal": 3500.0, "caaf": 150.0, "loyer_in": 588.0,
        "h_sup": 500.0, "rev_extra": 0.0,
        "l_out": 850.0, "a_emp": 200.0, "t_net": 90.0,
        "e_eau": 298.0, "mgen": 160.0, "kona": 415.0,
        "fam": 200.0, "a_vie": 50.0,
        "remboursement": 600.0, "obj_decouvert": 2000.0,
        "budget_bouffe": 600, "active_agathe": 0,
        "mode_urgence": 0, "last_report": 0.0
    }
    try:
        df = conn.read(worksheet="Config", ttl=0)
        if df is not None and not df.empty and "Variable" in df.columns:
            loaded = dict(zip(df["Variable"].astype(str), df["Valeur"]))
            for k, v in loaded.items():
                try:
                    defaults[k] = float(v)
                except (ValueError, TypeError):
                    pass
    except Exception as e:
        logger.warning(f"Impossible de charger Config: {e}")
    return defaults


def save_config(d: dict) -> bool:
    """Sauvegarde la config dans GSheets."""
    try:
        df = pd.DataFrame(list(d.items()), columns=["Variable", "Valeur"])
        conn.update(worksheet="Config", data=df)
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde Config: {e}")
        return False


def load_historique() -> pd.DataFrame:
    """Charge l'historique avec parsing robuste."""
    empty = pd.DataFrame(columns=["Date", "Nom", "Montant", "Type", "Mode"])
    try:
        df = conn.read(worksheet="Historique", ttl=0)
        if df is None or df.empty:
            return empty
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Montant"] = pd.to_numeric(df["Montant"], errors="coerce").fillna(0.0)
        df["Nom"]  = df.get("Nom",  pd.Series(dtype=str)).fillna("").astype(str)
        df["Type"] = df.get("Type", pd.Series(dtype=str)).fillna("Autre").astype(str)
        df["Mode"] = df.get("Mode", pd.Series(dtype=str)).fillna("Normal").astype(str)
        return df.reset_index(drop=True)
    except Exception as e:
        logger.error(f"Erreur chargement Historique: {e}")
        return empty


def save_historique(df: pd.DataFrame) -> bool:
    """Sauvegarde l'historique complet."""
    try:
        df_save = df.copy()
        df_save["Date"] = df_save["Date"].dt.strftime("%Y-%m-%d")
        conn.update(worksheet="Historique", data=df_save)
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde Historique: {e}")
        return False


def add_depense(df_h: pd.DataFrame, nom: str, montant: float, type_: str) -> pd.DataFrame:
    """Ajoute une dépense et sauvegarde."""
    new_row = pd.DataFrame([{
        "Date": pd.Timestamp(datetime.now().date()),
        "Nom": nom.strip(),
        "Montant": round(montant, 2),
        "Type": type_,
        "Mode": "Normal"
    }])
    df_new = pd.concat([df_h, new_row], ignore_index=True)
    return df_new

# ═══════════════════════════════════════════════
# CHARGEMENT DES DONNÉES
# ═══════════════════════════════════════════════
conf = load_config()
df_h = load_historique()
now  = datetime.now()

# ═══════════════════════════════════════════════
# SIDEBAR — RÉGLAGES
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 💸 Agathe Budget")
    st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

    with st.expander("💰 Revenus", expanded=False):
        sal      = st.number_input("Salaire Base (€)",    value=float(conf["sal"]),      step=50.0)
        caaf     = st.number_input("CAAF (€)",             value=float(conf["caaf"]),     step=10.0)
        loyer_in = st.number_input("Loyer Perçu (€)",     value=float(conf["loyer_in"]), step=10.0)
        h_sup    = st.number_input("Heures Sup (€)",      value=float(conf["h_sup"]),    step=50.0)
        rev_extra= st.number_input("Revenu Extra (€)",    value=float(conf["rev_extra"]),step=10.0)

    with st.expander("🏠 Charges Fixes", expanded=False):
        l_out = st.number_input("Loyer / Emprunt (€)",   value=float(conf["l_out"]), step=10.0)
        a_emp = st.number_input("Assurance Emprunt (€)", value=float(conf["a_emp"]), step=10.0)
        t_net = st.number_input("Tel + Internet (€)",    value=float(conf["t_net"]), step=5.0)
        e_eau = st.number_input("EDF + Eau (€)",         value=float(conf["e_eau"]), step=10.0)
        mgen  = st.number_input("MGEN (€)",              value=float(conf["mgen"]),  step=5.0)
        kona  = st.number_input("Kona + Assurance (€)",  value=float(conf["kona"]),  step=10.0)
        fam   = st.number_input("Famille (€)",           value=float(conf["fam"]),   step=10.0)
        a_vie = st.number_input("Assurance Vie (€)",     value=float(conf["a_vie"]), step=5.0)

    with st.expander("📉 Stratégie Découvert", expanded=True):
        remboursement = st.number_input("Remboursement ce mois (€)", value=float(conf["remboursement"]), step=50.0)
        obj_decouvert = st.number_input("Découvert Cible Total (€)", value=float(conf["obj_decouvert"]), step=100.0)
        budget_bouffe = st.slider("Budget Courses (€)", 300, 1000, int(conf["budget_bouffe"]))
        active_agathe = st.toggle("🏆 Trésor Agathe (1000€)", value=int(conf["active_agathe"]) == 1)
        mode_urgence  = st.toggle("🚨 Mode Vigilance",        value=int(conf["mode_urgence"])  == 1)

    # Report / Ajustement avec persistance cloud
    if "solde_ajustement" not in st.session_state:
        st.session_state.solde_ajustement = float(conf["last_report"])
    st.session_state.solde_ajustement = st.number_input(
        "🔁 Report / Ajustement (€)",
        value=st.session_state.solde_ajustement,
        step=1.0
    )

    st.markdown("")
    if st.button("💾 Sauvegarder Configuration", use_container_width=True):
        ok = save_config({
            "sal": sal, "caaf": caaf, "loyer_in": loyer_in, "h_sup": h_sup, "rev_extra": rev_extra,
            "l_out": l_out, "a_emp": a_emp, "t_net": t_net, "e_eau": e_eau, "mgen": mgen,
            "kona": kona, "fam": fam, "a_vie": a_vie,
            "remboursement": remboursement, "obj_decouvert": obj_decouvert,
            "budget_bouffe": budget_bouffe,
            "active_agathe": 1 if active_agathe else 0,
            "mode_urgence":  1 if mode_urgence  else 0,
            "last_report":   st.session_state.solde_ajustement
        })
        if ok:
            st.success("✅ Config sauvegardée !")
            st.cache_resource.clear()
        else:
            st.error("❌ Erreur de sauvegarde")

# ═══════════════════════════════════════════════
# MOTEUR DE CALCUL
# ═══════════════════════════════════════════════
rev_total     = sal + caaf + loyer_in + h_sup + rev_extra
charges_total = l_out + a_emp + t_net + e_eau + mgen + kona + fam + a_vie
epargne_agathe= 1000.0 if active_agathe else 0.0
coeff_urg     = 0.7 if mode_urgence else 1.0
jours_mois    = calendar.monthrange(now.year, now.month)[1]

budget_mois_dispo = rev_total - charges_total - remboursement - epargne_agathe - (budget_bouffe * coeff_urg)
obj_journalier    = budget_mois_dispo / jours_mois

# Filtres temporels robustes
def filter_month(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    if df.empty:
        return df
    mask = (df["Date"].apply(lambda x: x.year) == year) & \
           (df["Date"].apply(lambda x: x.month) == month)
    return df[mask].copy()

df_mois = filter_month(df_h, now.year, now.month)

total_depenses_mois = df_mois["Montant"].sum() if not df_mois.empty else 0.0
depense_ajd = df_mois[df_mois["Date"].apply(lambda x: x.date()) == now.date()]["Montant"].sum() \
              if not df_mois.empty else 0.0
reste_jour  = obj_journalier + st.session_state.solde_ajustement - depense_ajd
fin_mois    = (budget_mois_dispo + st.session_state.solde_ajustement) - total_depenses_mois

# ═══════════════════════════════════════════════
# EN-TÊTE PRINCIPAL
# ═══════════════════════════════════════════════
col_title, col_mode = st.columns([3, 1])
with col_title:
    st.title(f"💸 Agathe Budget")
    st.markdown(f"**{now.strftime('%A %d %B %Y')}** · Jour {now.day}/{jours_mois}", unsafe_allow_html=False)
with col_mode:
    if mode_urgence:
        st.markdown('<div class="fun-alert-danger">🚨 <b>MODE VIGILANCE</b><br><small>Budget réduit à 70%</small></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="fun-alert-success">✅ <b>MODE NORMAL</b><br><small>Budget complet actif</small></div>', unsafe_allow_html=True)

st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PROGRESSION REMBOURSEMENT
# ═══════════════════════════════════════════════
progress_pct = min(1.0, remboursement / max(obj_decouvert, 1))
progress_color = "#1DD1A1" if progress_pct >= 0.7 else "#FF9F43" if progress_pct >= 0.4 else "#FF6B9D"

st.markdown("### 🎯 Progression Remboursement Découvert")
st.markdown(f"""
<div style="margin-bottom:4px; display:flex; justify-content:space-between;">
    <span style="color:var(--muted); font-size:0.85rem;">0 €</span>
    <span style="color:{progress_color}; font-weight:800; font-size:1rem;">{progress_pct*100:.1f}% — {remboursement:.0f} € / {obj_decouvert:.0f} €</span>
    <span style="color:var(--muted); font-size:0.85rem;">{obj_decouvert:.0f} €</span>
</div>
<div class="progress-wrap">
    <div class="progress-fill" style="width:{progress_pct*100:.1f}%; background:linear-gradient(90deg, {progress_color}, #FECA57);"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# MÉTRIQUES CLÉS
# ═══════════════════════════════════════════════
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("🎯 Objectif / Jour", f"{obj_journalier:.2f} €")
with m2:
    delta_color = "normal" if reste_jour >= 0 else "inverse"
    st.metric("💳 Dispo Aujourd'hui", f"{reste_jour:.2f} €",
              delta=f"Report: {st.session_state.solde_ajustement:+.2f}€",
              delta_color=delta_color)
with m3:
    delta_fin = "normal" if fin_mois >= 0 else "inverse"
    st.metric("📅 Fin de Mois Prévu", f"{fin_mois:.2f} €", delta_color=delta_fin)
with m4:
    st.metric("🛒 Dépenses du Mois", f"{total_depenses_mois:.2f} €",
              delta=f"{total_depenses_mois - budget_mois_dispo:.2f} € vs budget")

# Alerte si dépassement
if reste_jour < 0:
    st.markdown(f'<div class="fun-alert-danger">😬 <b>Attention !</b> Tu as dépassé ton budget journalier de <b>{abs(reste_jour):.2f} €</b>. Tiens bon !</div>', unsafe_allow_html=True)
elif reste_jour > obj_journalier * 1.5:
    st.markdown(f'<div class="fun-alert-success">🎉 <b>Super !</b> Tu as {reste_jour:.2f} € disponibles aujourd'hui — tu gères !</div>', unsafe_allow_html=True)

st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# GRAPHIQUES
# ═══════════════════════════════════════════════
g1, g2 = st.columns([3, 2])

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F0EEF8", family="Nunito"),
    margin=dict(l=10, r=10, t=30, b=10),
)
COLORS = ["#FF6B9D", "#FF9F43", "#FECA57", "#1DD1A1", "#54A0FF", "#A29BFE"]

with g1:
    st.markdown("### 📈 Évolution des Dépenses")
    if not df_mois.empty:
        df_plot = df_mois.copy()
        df_plot["DateStr"] = df_plot["Date"].dt.strftime("%d/%m")
        df_agg = df_plot.groupby("DateStr")["Montant"].sum().reset_index()
        df_agg["Cumulé"] = df_agg["Montant"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_agg["DateStr"], y=df_agg["Montant"],
            name="Dépenses/Jour",
            marker=dict(color="#FF6B9D", opacity=0.7, line=dict(color="#FF6B9D", width=0)),
        ))
        fig.add_trace(go.Scatter(
            x=df_agg["DateStr"], y=df_agg["Cumulé"],
            name="Cumulé", mode="lines+markers",
            line=dict(color="#FECA57", width=3),
            marker=dict(size=7, color="#FECA57")
        ))
        # Ligne budget mois
        fig.add_hline(y=budget_mois_dispo, line_dash="dot",
                      line_color="#1DD1A1", annotation_text="Budget Mois",
                      annotation_font_color="#1DD1A1")
        fig.update_layout(**CHART_LAYOUT, legend=dict(
            bgcolor="rgba(42,39,64,0.8)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1))
        fig.update_xaxes(showgrid=False, tickfont=dict(color="#9E9BBF"))
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#9E9BBF"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="fun-alert">📭 Aucune dépense ce mois-ci. C'est le bon début !</div>', unsafe_allow_html=True)

with g2:
    st.markdown("### 🍩 Répartition par Catégorie")
    if not df_mois.empty:
        fig2 = px.pie(
            df_mois.groupby("Type")["Montant"].sum().reset_index(),
            values="Montant", names="Type", hole=0.55,
            color_discrete_sequence=COLORS
        )
        fig2.update_traces(
            textfont=dict(color="white", size=12),
            marker=dict(line=dict(color="#1E1B2E", width=3))
        )
        fig2.update_layout(
            **CHART_LAYOUT,
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F0EEF8")),
            annotations=[dict(text=f"<b>{total_depenses_mois:.0f}€</b>",
                              x=0.5, y=0.5, font_size=20, font_color="#FECA57",
                              showarrow=False, font_family="Fredoka One")]
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown('<div class="fun-alert">📭 Aucune catégorie à afficher.</div>', unsafe_allow_html=True)

st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TABS PRINCIPAUX
# ═══════════════════════════════════════════════
CATEGORIES = ["Courses", "Vie Courante", "Loisirs", "Santé", "Imprévu", "Autre"]

tab1, tab2, tab3, tab4 = st.tabs(["✍️  Nouvelle Dépense", "📑  Historique", "📊  Multi-Mois", "⚙️  Archives"])

# ── TAB 1 : SAISIE ──────────────────────────────
with tab1:
    st.markdown("### ✍️ Ajouter une Dépense")

    with st.form("form_depense", clear_on_submit=True):
        col_a, col_b, col_c = st.columns([3, 2, 2])
        with col_a:
            nom_dep = st.text_input("📝 Désignation", placeholder="Ex: Intermarché, Restau, ...")
        with col_b:
            mnt_dep = st.number_input("💶 Montant (€)", min_value=0.01, step=0.5, format="%.2f")
        with col_c:
            type_dep = st.selectbox("🏷️ Catégorie", CATEGORIES)

        submitted = st.form_submit_button("➕ Valider la dépense", use_container_width=True)

        if submitted:
            errors = []
            if not nom_dep.strip():
                errors.append("Le champ **Désignation** est obligatoire.")
            if mnt_dep <= 0:
                errors.append("Le **Montant** doit être supérieur à 0 €.")

            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                df_new = add_depense(df_h, nom_dep, mnt_dep, type_dep)
                if save_historique(df_new):
                    st.success(f"✅ **{nom_dep.strip()}** — {mnt_dep:.2f} € ajouté !")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la sauvegarde. Réessaie.")

    # Dernières dépenses du jour
    if not df_mois.empty:
        df_ajd = df_mois[df_mois["Date"].apply(lambda x: x.date()) == now.date()]
        if not df_ajd.empty:
            st.markdown(f"**Aujourd'hui : {depense_ajd:.2f} € dépensés**")
            st.dataframe(
                df_ajd[["Nom", "Montant", "Type"]].sort_values("Montant", ascending=False),
                use_container_width=True, hide_index=True
            )


# ── TAB 2 : HISTORIQUE ──────────────────────────
with tab2:
    st.markdown("### 📑 Historique Complet")

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filtre_cat = st.multiselect("Filtrer par catégorie", CATEGORIES, default=CATEGORIES)
    with col_filter2:
        filtre_mois_options = []
        if not df_h.empty:
            df_h["_ym"] = df_h["Date"].apply(lambda x: f"{x.year}-{x.month:02d}")
            filtre_mois_options = sorted(df_h["_ym"].unique(), reverse=True)
        filtre_mois = st.selectbox("Filtrer par mois", ["Tous"] + filtre_mois_options)

    df_display = df_h.copy()
    if filtre_cat:
        df_display = df_display[df_display["Type"].isin(filtre_cat)]
    if filtre_mois != "Tous":
        df_display = df_display[df_display["_ym"] == filtre_mois]

    if "_ym" in df_display.columns:
        df_display = df_display.drop(columns=["_ym"])

    st.dataframe(
        df_display.sort_values("Date", ascending=False).assign(
            Date=lambda d: d["Date"].dt.strftime("%d/%m/%Y")
        ),
        use_container_width=True,
        hide_index=True
    )

    # CLÔTURE JOURNÉE — avec persistance cloud
    st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🌙 Clôture de Journée")
    st.markdown(f"Report calculé : **{reste_jour:.2f} €** (sera sauvegardé dans le cloud)")

    col_cl1, col_cl2 = st.columns(2)
    with col_cl1:
        if st.button("🌙 Clôturer & Sauvegarder le Report", use_container_width=True):
            st.session_state.solde_ajustement = reste_jour
            # Sauvegarde dans le cloud pour persistance
            new_conf = dict(conf)
            new_conf.update({
                "sal": sal, "caaf": caaf, "loyer_in": loyer_in, "h_sup": h_sup, "rev_extra": rev_extra,
                "l_out": l_out, "a_emp": a_emp, "t_net": t_net, "e_eau": e_eau, "mgen": mgen,
                "kona": kona, "fam": fam, "a_vie": a_vie,
                "remboursement": remboursement, "obj_decouvert": obj_decouvert,
                "budget_bouffe": budget_bouffe,
                "active_agathe": 1 if active_agathe else 0,
                "mode_urgence":  1 if mode_urgence  else 0,
                "last_report":   reste_jour
            })
            if save_config(new_conf):
                st.success(f"✅ Journée clôturée ! Report de **{reste_jour:.2f} €** sauvegardé.")
            else:
                st.error("❌ Erreur lors de la sauvegarde du report.")
            st.rerun()
    with col_cl2:
        if st.button("🔄 Reset Report à 0", use_container_width=True):
            st.session_state.solde_ajustement = 0.0
            new_conf = dict(conf)
            new_conf["last_report"] = 0.0
            save_config(new_conf)
            st.rerun()


# ── TAB 3 : MULTI-MOIS ──────────────────────────
with tab3:
    st.markdown("### 📊 Analyse Multi-Mois")

    if df_h.empty:
        st.markdown('<div class="fun-alert">📭 Pas encore de données historiques.</div>', unsafe_allow_html=True)
    else:
        df_multi = df_h.copy()
        df_multi["Mois"]   = df_multi["Date"].apply(lambda x: f"{x.year}-{x.month:02d}")
        df_multi["MoisFr"] = df_multi["Date"].apply(lambda x: f"{calendar.month_abbr[x.month]} {x.year}")

        # Synthèse par mois
        synth = df_multi.groupby("Mois").agg(
            Total=("Montant", "sum"),
            NbOp=("Montant", "count"),
            Moyenne=("Montant", "mean")
        ).reset_index().sort_values("Mois")
        synth["MoisFr"] = synth["Mois"].apply(
            lambda m: f"{calendar.month_abbr[int(m.split('-')[1])]} {m.split('-')[0]}"
        )

        # Graphique évolution mensuelle
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Bar(
            x=synth["MoisFr"], y=synth["Total"],
            marker=dict(
                color=synth["Total"],
                colorscale=[[0, "#1DD1A1"], [0.5, "#FECA57"], [1, "#FF6B9D"]],
                showscale=False
            ),
            name="Total Mois"
        ))
        fig_multi.add_trace(go.Scatter(
            x=synth["MoisFr"], y=synth["Total"].rolling(3, min_periods=1).mean(),
            name="Moyenne 3 mois", mode="lines",
            line=dict(color="#A29BFE", width=2, dash="dot")
        ))
        fig_multi.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Dépenses Totales par Mois", font=dict(color="#F0EEF8")),
            legend=dict(bgcolor="rgba(42,39,64,0.8)")
        )
        fig_multi.update_xaxes(showgrid=False, tickfont=dict(color="#9E9BBF"))
        fig_multi.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#9E9BBF"))
        st.plotly_chart(fig_multi, use_container_width=True)

        # Répartition par catégorie et par mois
        st.markdown("#### 🏷️ Répartition par Catégorie")
        pivot = df_multi.pivot_table(
            index="Mois", columns="Type", values="Montant", aggfunc="sum", fill_value=0
        ).reset_index()
        pivot["MoisFr"] = pivot["Mois"].apply(
            lambda m: f"{calendar.month_abbr[int(m.split('-')[1])]} {m.split('-')[0]}"
        )

        fig_stacked = go.Figure()
        for i, col in enumerate([c for c in pivot.columns if c not in ["Mois", "MoisFr"]]):
            fig_stacked.add_trace(go.Bar(
                x=pivot["MoisFr"], y=pivot[col],
                name=col, marker_color=COLORS[i % len(COLORS)]
            ))
        fig_stacked.update_layout(
            **CHART_LAYOUT, barmode="stack",
            legend=dict(bgcolor="rgba(42,39,64,0.8)")
        )
        fig_stacked.update_xaxes(showgrid=False, tickfont=dict(color="#9E9BBF"))
        fig_stacked.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#9E9BBF"))
        st.plotly_chart(fig_stacked, use_container_width=True)

        # Tableau récap
        st.markdown("#### 📋 Récapitulatif Mensuel")
        st.dataframe(
            synth[["MoisFr", "Total", "NbOp", "Moyenne"]].rename(columns={
                "MoisFr": "Mois", "Total": "Total (€)", "NbOp": "Nb Opérations", "Moyenne": "Moy/Op (€)"
            }).assign(**{
                "Total (€)": lambda d: d["Total (€)"].round(2),
                "Moy/Op (€)": lambda d: d["Moy/Op (€)"].round(2)
            }).sort_values("Mois", ascending=False),
            use_container_width=True, hide_index=True
        )


# ── TAB 4 : ARCHIVES ────────────────────────────
with tab4:
    st.markdown("### ⚙️ Archivage des Données")

    st.markdown('<div class="fun-alert">ℹ️ L\'archivage copie l\'historique complet dans l\'onglet <b>Archives</b> de ton Google Sheet.</div>', unsafe_allow_html=True)

    col_arch1, col_arch2 = st.columns(2)
    with col_arch1:
        confirm_arch = st.checkbox("✅ Je confirme vouloir archiver les données actuelles")
        if st.button("📦 Archiver l'Historique", disabled=not confirm_arch, use_container_width=True):
            try:
                df_arch_old = conn.read(worksheet="Archives", ttl=0)
                df_arch_old = df_arch_old if df_arch_old is not None and not df_arch_old.empty else pd.DataFrame()
                df_to_archive = df_h.copy()
                df_to_archive["Date"] = df_to_archive["Date"].dt.strftime("%Y-%m-%d")
                df_merged = pd.concat([df_arch_old, df_to_archive], ignore_index=True)
                conn.update(worksheet="Archives", data=df_merged)
                st.success("✅ Données archivées avec succès !")
            except Exception as e:
                st.error(f"❌ Erreur : {e}. Vérifie que l'onglet 'Archives' existe dans ton Google Sheet.")

    with col_arch2:
        st.markdown("**📊 Stats de l'Historique actuel**")
        if not df_h.empty:
            st.markdown(f"- **{len(df_h)}** opérations au total")
            st.markdown(f"- **{df_h['Montant'].sum():.2f} €** dépensés en tout")
            if not df_h["Date"].isna().all():
                st.markdown(f"- Du **{df_h['Date'].min().strftime('%d/%m/%Y')}** au **{df_h['Date'].max().strftime('%d/%m/%Y')}**")
        else:
            st.markdown("Aucune donnée dans l'historique.")

# ═══════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════
st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)
st.markdown(
    f'<p style="text-align:center; color:var(--muted); font-size:0.8rem;">'
    f'💸 Agathe Budget · DNA-Beat · {now.strftime("%Y")} · '
    f'Revenus : <b style="color:#1DD1A1">{rev_total:.0f} €</b> · '
    f'Charges : <b style="color:#FF6B9D">{charges_total:.0f} €</b> · '
    f'Budget mois : <b style="color:#FECA57">{budget_mois_dispo:.0f} €</b>'
    f'</p>',
    unsafe_allow_html=True
)

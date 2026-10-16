import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Tableau de bord – Support IT",
    page_icon="🎫",
    layout="wide",
)
# -------------------- Path File ("01_Technologie_IT.xlsx") --------------------
DATA_FILE = Path(__file__).with_name("01_Technologie_IT.xlsx")


@st.cache_data
def load_data():
    # The real column headers are on row 2 of the Excel sheet.
    df = pd.read_excel(DATA_FILE, sheet_name="Données", header=1)
    df = df.iloc[:, :12].copy()
    df.columns = [
        "ID ticket", "Date ouverture", "Ville", "Service", "Canal",
        "Type de demande", "Priorité", "Réponse (h)", "Résolution (h)",
        "Statut", "Objectif SLA (h)", "Satisfaction /5"
    ]

    # Remove accidental/empty rows and keep only real ticket IDs.
    df = df[df["ID ticket"].astype(str).str.startswith("IT-")].copy()

    df["Date ouverture"] = pd.to_datetime(df["Date ouverture"], errors="coerce")
    for col in ["Réponse (h)", "Résolution (h)", "Objectif SLA (h)", "Satisfaction /5"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Mois"] = df["Date ouverture"].dt.to_period("M").astype("string")

    # SLA is evaluated only for resolved tickets.
    df["SLA dépassé"] = (
        (df["Statut"].eq("Résolu"))
        & df["Résolution (h)"].notna()
        & df["Objectif SLA (h)"].notna()
        & (df["Résolution (h)"] > df["Objectif SLA (h)"])
    )
    return df


df = load_data()

st.title("🎫 Tableau de bord – Tickets de support informatique")
st.caption("Entreprise de services numériques fictive · janvier–août 2026 · 800 tickets")

# -------------------- Sidebar filters --------------------
st.sidebar.header("Filtres")

def multiselect_with_all(label, series):
    options = sorted(series.dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, options, default=options)

services = multiselect_with_all("Service", df["Service"])
priorities = multiselect_with_all("Priorité", df["Priorité"])
channels = multiselect_with_all("Canal", df["Canal"])
statuses = multiselect_with_all("Statut", df["Statut"])

date_min = df["Date ouverture"].min().date()
date_max = df["Date ouverture"].max().date()
date_range = st.sidebar.date_input(
    "Période",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

mask = (
    df["Service"].isin(services)
    & df["Priorité"].isin(priorities)
    & df["Canal"].isin(channels)
    & df["Statut"].isin(statuses)
    & df["Date ouverture"].dt.date.between(start_date, end_date)
)
f = df.loc[mask].copy()

resolved = f[f["Statut"].eq("Résolu")].copy()

# -------------------- KPIs --------------------
total = len(f)
resolved_n = len(resolved)
sla_n = int(resolved["SLA dépassé"].sum()) if resolved_n else 0
sla_rate = sla_n / resolved_n if resolved_n else float("nan")
median_response = f["Réponse (h)"].median()
median_resolution = resolved["Résolution (h)"].median()
satisfaction = resolved["Satisfaction /5"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tickets", f"{total:,}".replace(",", " "))
k2.metric("Tickets résolus", f"{resolved_n:,}".replace(",", " "))
k3.metric("SLA dépassé", f"{sla_rate:.1%}" if pd.notna(sla_rate) else "N/A")
k4.metric("Réponse médiane", f"{median_response:.1f} h" if pd.notna(median_response) else "N/A")

st.divider()

# -------------------- Questions 1–3 --------------------
st.subheader("1. Types de demandes les plus fréquents")

type_counts = f["Type de demande"].value_counts()
if not type_counts.empty:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    type_counts.sort_values().plot(kind="barh", ax=ax)
    ax.set_xlabel("Nombre de tickets")
    ax.set_ylabel("")
    ax.set_title("Volume des tickets par type de demande")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    top_type = type_counts.index[0]
    st.write(
        f"Le type **{top_type}** est le plus représenté avec **{int(type_counts.iloc[0])} tickets** "
        f"({type_counts.iloc[0] / total:.1%} du périmètre filtré)."
    )
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

st.subheader("2. Service recevant le plus de tickets et délai médian de résolution")

service_counts = f["Service"].value_counts()
if not service_counts.empty:
    top_service = service_counts.index[0]
    top_service_res = resolved.loc[
        resolved["Service"].eq(top_service), "Résolution (h)"
    ].median()

    c1, c2 = st.columns(2)
    c1.metric("Service n°1", f"{top_service} – {int(service_counts.iloc[0])} tickets")
    c2.metric(
        "Délai médian de résolution",
        f"{top_service_res:.1f} h" if pd.notna(top_service_res) else "N/A",
    )
    st.write(
        f"**{top_service}** reçoit le plus de tickets. Son délai médian de résolution "
        f"est de **{top_service_res:.1f} h** parmi les tickets résolus."
        if pd.notna(top_service_res)
        else f"**{top_service}** reçoit le plus de tickets, mais aucun ticket résolu "
             "n'est disponible dans le périmètre sélectionné."
    )

st.subheader("3. Part des tickets résolus dépassant le SLA")

if resolved_n:
    by_priority = (
        resolved.groupby("Priorité")["SLA dépassé"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "Dépassements", "count": "Résolus", "mean": "Taux"})
    )
    by_priority["Taux"] = by_priority["Taux"] * 100
    st.dataframe(
        by_priority[["Dépassements", "Résolus", "Taux"]].style.format({"Taux": "{:.1f}%"}),
        use_container_width=True,
    )
    st.write(
        f"Au total, **{sla_n} tickets sur {resolved_n} résolus ({sla_rate:.1%})** "
        "dépassent l'objectif SLA. Le dénominateur est bien limité aux tickets résolus."
    )
else:
    st.info("Aucun ticket résolu dans le périmètre sélectionné.")

# -------------------- Question 4 --------------------
st.subheader("4. Les canaux diffèrent-ils en temps de première réponse ?")

channel_stats = f.groupby("Canal")["Réponse (h)"].median().sort_values()
if not channel_stats.empty:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    channel_stats.plot(kind="bar", ax=ax)
    ax.set_ylabel("Médiane de première réponse (heures)")
    ax.set_xlabel("")
    ax.set_title("Temps médian de première réponse par canal")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    fastest = channel_stats.index[0]
    slowest = channel_stats.index[-1]
    st.write(
        f"Dans cet échantillon, **{fastest}** a la médiane de première réponse la plus courte "
        f"({channel_stats.iloc[0]:.1f} h), contre **{channel_stats.iloc[-1]:.1f} h** pour "
        f"**{slowest}**. Cette comparaison est descriptive : elle ne prouve pas que le canal "
        "cause à lui seul la différence, car la priorité, le type de demande et la charge "
        "peuvent aussi influencer les délais."
    )

# -------------------- Question 5 --------------------
st.subheader("5. Évolution mensuelle du volume et des dépassements SLA")

monthly = (
    f.groupby("Mois")
    .agg(
        Tickets=("ID ticket", "count"),
        Résolus=("Statut", lambda s: (s == "Résolu").sum()),
        Dépassements_SLA=("SLA dépassé", "sum"),
    )
    .sort_index()
)

if not monthly.empty:
    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    ax1.plot(monthly.index, monthly["Tickets"], marker="o", label="Tickets")
    ax1.plot(monthly.index, monthly["Dépassements_SLA"], marker="o", label="Dépassements SLA")
    ax1.set_ylabel("Nombre de tickets")
    ax1.set_xlabel("Mois")
    ax1.set_title("Volume mensuel et dépassements SLA")
    ax1.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(monthly, use_container_width=True)

# -------------------- Question 6 --------------------
st.subheader("6. Recommandation au responsable du support")

# Recommendation is calculated from the current filtered data.
if not type_counts.empty and resolved_n:
    worst_priority = by_priority["Taux"].idxmax() if not by_priority.empty else None
    worst_priority_rate = by_priority.loc[worst_priority, "Taux"] if worst_priority else None

    st.markdown(
        f"""
**Action proposée : renforcer en priorité le traitement des demandes les plus fréquentes
et mettre en place un suivi quotidien des SLA.**

Le volume est dominé par **{type_counts.index[0]} ({int(type_counts.iloc[0])} tickets)**.
Par ailleurs, **{sla_rate:.1%}** des tickets résolus dépassent leur objectif SLA.
La priorité présentant le taux de dépassement le plus élevé dans le périmètre filtré est
**{worst_priority} ({worst_priority_rate:.1f}%)**.

Je recommande donc de créer une file de traitement prioritaire pour les demandes récurrentes,
avec une alerte avant échéance SLA et un suivi hebdomadaire par service et priorité.
"""
    )
else:
    st.info("Élargissez les filtres pour obtenir une recommandation chiffrée.")

with st.expander("Voir les données filtrées"):
    st.dataframe(f, use_container_width=True)

st.caption(
    "Méthode : les valeurs manquantes de résolution et de satisfaction ne sont pas remplacées "
    "par zéro. Le dépassement SLA est calculé uniquement sur les tickets résolus : "
    "Résolution (h) > Objectif SLA (h)."
)

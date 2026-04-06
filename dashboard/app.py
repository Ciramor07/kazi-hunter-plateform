import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = os.getenv("DB_PATH", "/app/data/kazi.db")

st.set_page_config(
    page_title="Kazi Hunter",
    page_icon="🎯",
    layout="wide"
)

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def load_offers(status_filter=None, platform_filter=None, min_score=0):
    conn = get_connection()
    query = "SELECT * FROM offers WHERE score >= ?"
    params = [min_score]

    if status_filter and status_filter != "Tous":
        query += " AND status = ?"
        params.append(status_filter.lower())

    if platform_filter and platform_filter != "Toutes":
        query += " AND platform = ?"
        params.append(platform_filter.lower())

    query += " ORDER BY score DESC, created_at DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_status(offer_id, new_status):
    conn = get_connection()
    conn.execute("UPDATE offers SET status = ? WHERE id = ?", (new_status, offer_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    stats = {}
    stats["total"]    = pd.read_sql_query("SELECT COUNT(*) as c FROM offers", conn)["c"][0]
    stats["new"]      = pd.read_sql_query("SELECT COUNT(*) as c FROM offers WHERE status='new'", conn)["c"][0]
    stats["reviewed"] = pd.read_sql_query("SELECT COUNT(*) as c FROM offers WHERE status='reviewed'", conn)["c"][0]
    stats["applied"]  = pd.read_sql_query("SELECT COUNT(*) as c FROM offers WHERE status='applied'", conn)["c"][0]
    stats["avg_score"]= pd.read_sql_query("SELECT AVG(score) as s FROM offers WHERE score > 0", conn)["s"][0]
    conn.close()
    return stats

# ── Header ────────────────────────────────────────────────
st.title("🎯 Kazi Hunter — Dashboard")
st.markdown("---")

# ── Stats ─────────────────────────────────────────────────
stats = get_stats()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total offres",    stats["total"])
c2.metric("🆕 Nouvelles",       stats["new"])
c3.metric("👀 Consultées",      stats["reviewed"])
c4.metric("📤 Candidatures",    stats["applied"])
c5.metric("⭐ Score moyen",     f"{stats['avg_score']:.1f}/10" if stats["avg_score"] else "N/A")

st.markdown("---")

# ── Filtres ───────────────────────────────────────────────
st.subheader("🔍 Filtres")
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Statut",
        ["Tous", "New", "Reviewed", "Applied", "Rejected"]
    )

with col2:
    platform_filter = st.selectbox(
        "Plateforme",
        ["Toutes", "Indeed", "LinkedIn", "WTTJ"]
    )

with col3:
    min_score = st.slider("Score minimum", 0.0, 10.0, 5.0, 0.5)

st.markdown("---")

# ── Liste des offres ──────────────────────────────────────
df = load_offers(status_filter, platform_filter, min_score)
st.subheader(f"📋 {len(df)} offres trouvées")

if df.empty:
    st.info("Aucune offre trouvée avec ces filtres.")
else:
    for _, row in df.iterrows():

        # Couleur selon score
        if row["score"] >= 8:
            color = "🟢"
        elif row["score"] >= 6:
            color = "🟡"
        else:
            color = "🔴"

        with st.expander(f"{color} {row['score']}/10 — {row['title']} @ {row['company']} ({row['platform'].upper()})"):

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**📍 Localisation** : {row['location']}")
                st.markdown(f"**💼 Contrat** : {row['contract']}")
                st.markdown(f"**💰 Salaire** : {row['salary']}")
                st.markdown(f"**🤖 Analyse IA** : {row['notes'] or 'Non scorée'}")
                if row["url"]:
                    st.markdown(f"**🔗 [Voir l'offre]({row['url']})**")

            with col2:
                st.markdown(f"**Statut actuel** : `{row['status']}`")
                new_status = st.selectbox(
                    "Changer statut",
                    ["new", "reviewed", "applied", "rejected"],
                    index=["new", "reviewed", "applied", "rejected"].index(row["status"]) if row["status"] in ["new", "reviewed", "applied", "rejected"] else 0,
                    key=f"status_{row['id']}"
                )
                if st.button("💾 Sauvegarder", key=f"save_{row['id']}"):
                    update_status(row["id"], new_status)
                    st.success("✅ Statut mis à jour !")
                    st.rerun()

st.markdown("---")
st.caption("Kazi Hunter v0.1 — Powered by Ollama + Mistral 7B")

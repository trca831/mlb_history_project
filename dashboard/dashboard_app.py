import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="MLB History Dashboard", layout="wide")
st.title(" MLB History Dashboard")
st.markdown("Explore MLB history — player stats, yearly events, and performance trends!")

# --- CONNECT TO DATABASE ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("mlb_history.db")
    years = pd.read_sql("SELECT * FROM years", conn)
    events = pd.read_sql("SELECT * FROM events", conn)
    stats = pd.read_sql("SELECT * FROM statistics", conn)
    conn.close()
    return years, events, stats

years_df, events_df, stats_df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("⚙️ Filters")

# Combine all years from both tables
all_years = sorted(set(stats_df["Year"]).union(set(events_df["Year"])), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", all_years)

# Safe category selector
all_categories = sorted(stats_df["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Stat Category", all_categories)

# Filter datasets safely (handle missing years)
filtered_stats = stats_df[stats_df["Year"] == selected_year] if selected_year in stats_df["Year"].values else pd.DataFrame()
filtered_events = events_df[events_df["Year"] == selected_year] if selected_year in events_df["Year"].values else pd.DataFrame()

# --- TOP 5 PLAYERS (BAR) ---
st.subheader(f" Top 5 Players — {selected_category} ({selected_year})")

if not filtered_stats.empty:
    filtered_stats = filtered_stats[filtered_stats["Category"] == selected_category].copy()
    filtered_stats["Value"] = pd.to_numeric(filtered_stats["Value"], errors="coerce")
    filtered_stats = filtered_stats.dropna(subset=["Value"])

    if not filtered_stats.empty:
        top_players = filtered_stats.nlargest(5, "Value")
        fig1 = px.bar(
            top_players,
            x="Player",
            y="Value",
            color="Player",
            text="Value",
            title=f"Top 5 {selected_category} Leaders ({selected_year})"
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No numeric data available for this category/year.")
else:
    st.warning("No player statistics available for this year.")

# --- PIE CHART: EVENT DISTRIBUTION ---
st.subheader(f" Event Breakdown for {selected_year}")

if not filtered_events.empty:
    events_pie = filtered_events.groupby("Event").size().reset_index(name="Count")
    fig_pie = px.pie(
        events_pie,
        names="Event",
        values="Count",
        hole=0.4,
        title=f"Event Category Distribution in {selected_year}"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Optional: show event descriptions too
    with st.expander(f"View detailed events for {selected_year}"):
        for _, row in filtered_events.iterrows():
            st.markdown(f"**{row['Event']}** — {row['Description']}")
else:
    st.info("No major events available for this year.")

# --- SCATTER PLOT: PLAYER PERFORMANCE SPREAD ---
st.subheader(f" Player Performance Spread — {selected_category} ({selected_year})")

if not filtered_stats.empty:
    scatter_data = filtered_stats.copy()
    scatter_data["Value"] = pd.to_numeric(scatter_data["Value"], errors="coerce")
    scatter_data = scatter_data.dropna(subset=["Value"])

    if not scatter_data.empty:
        fig_scatter = px.scatter(
            scatter_data,
            x="Player",
            y="Value",
            size="Value",
            color="Value",
            hover_name="Player",
            title=f"{selected_category} Distribution for {selected_year}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No scatter data for this category/year.")
else:
    st.warning("No player data to display in scatter plot.")

# --- TREND OVER TIME ---
st.subheader(f" {selected_category} Trends Over Time")

trend_data = stats_df[stats_df["Category"] == selected_category].copy()
trend_data["Value"] = pd.to_numeric(trend_data["Value"], errors="coerce")
trend_data = trend_data.dropna(subset=["Value"])

if not trend_data.empty:
    avg_trend = trend_data.groupby("Year")["Value"].mean().reset_index()
    fig2 = px.line(
        avg_trend,
        x="Year",
        y="Value",
        markers=True,
        title=f"Average {selected_category} Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No trend data available for this category.")

# --- FOOTER ---
st.markdown("---")
st.caption("Created by Tracy Cano | Data from Baseball Almanac")


import streamlit as st
import oracledb
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="IPL Analytics",
    page_icon="📊",
    layout="wide"
)

load_dotenv()

def get_connection():
    dsn = oracledb.makedsn(
        os.getenv("DB_HOST"),
        int(os.getenv("DB_PORT")),
        service_name=os.getenv("DB_SERVICE")
    )

    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=dsn
    )


@st.cache_data
def load_data():

    conn = get_connection()

    matches = pd.read_sql("""
        SELECT
            SEASON,
            MATCH_ID,
            WINNER_TEAM_ID,
            TEAM1_ID,
            TEAM2_ID
        FROM MATCHES
    """, conn)

    teams = pd.read_sql("""
        SELECT TEAM_ID, TEAM_NAME
        FROM TEAMS
    """, conn)

    players = pd.read_sql("""
        SELECT
            P.PLAYER_ID,
            P.PLAYER_NAME,
            SUM(S.RUNS) AS TOTAL_RUNS,
            SUM(S.WICKETS) AS TOTAL_WICKETS
        FROM PLAYERS P
        LEFT JOIN PLAYER_MATCH_STATS S
            ON P.PLAYER_ID = S.PLAYER_ID
        GROUP BY P.PLAYER_ID, P.PLAYER_NAME
    """, conn)

    conn.close()

    return matches, teams, players


try:

    matches, teams, players = load_data()

    st.title("📊 IPL Advanced Analytics")
    st.write("Discover patterns, trends and performance across IPL seasons.")

    # -------------------------
    # 1. MATCHES PER SEASON
    # -------------------------

    st.subheader("1. Matches Played Per Season")

    season_data = (
        matches.groupby("SEASON")["MATCH_ID"]
        .nunique()
        .reset_index(name="MATCHES")
        .sort_values("SEASON")
    )

    fig1 = px.bar(
        season_data,
        x="SEASON",
        y="MATCHES",
        title="Number of Matches in Each IPL Season",
        text="MATCHES"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # -------------------------
    # 2. TOP RUN SCORERS
    # -------------------------

    st.subheader("2. Top 10 Run Scorers")

    top_runs = players.nlargest(10, "TOTAL_RUNS")

    fig2 = px.bar(
        top_runs.sort_values("TOTAL_RUNS"),
        x="TOTAL_RUNS",
        y="PLAYER_NAME",
        orientation="h",
        title="Top 10 IPL Run Scorers",
        text="TOTAL_RUNS"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------
    # 3. TOP WICKET TAKERS
    # -------------------------

    st.subheader("3. Top 10 Wicket Takers")

    top_wickets = players.nlargest(10, "TOTAL_WICKETS")

    fig3 = px.bar(
        top_wickets.sort_values("TOTAL_WICKETS"),
        x="TOTAL_WICKETS",
        y="PLAYER_NAME",
        orientation="h",
        title="Top 10 IPL Wicket Takers",
        text="TOTAL_WICKETS"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # -------------------------
    # 4. TEAM WIN COUNTS
    # -------------------------

    st.subheader("4. Most Successful IPL Teams")

    wins = (
        matches.groupby("WINNER_TEAM_ID")["MATCH_ID"]
        .count()
        .reset_index(name="WINS")
    )

    wins = wins.merge(
        teams,
        left_on="WINNER_TEAM_ID",
        right_on="TEAM_ID",
        how="left"
    )

    wins = wins.dropna(subset=["TEAM_NAME"])

    fig4 = px.bar(
        wins.sort_values("WINS"),
        x="WINS",
        y="TEAM_NAME",
        orientation="h",
        title="Total Wins by Team",
        text="WINS"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------
    # 5. TEAM WIN PERCENTAGE
    # -------------------------

    st.subheader("5. Team Win Percentage")

    all_matches = pd.concat([
        matches[["TEAM1_ID"]].rename(columns={"TEAM1_ID": "TEAM_ID"}),
        matches[["TEAM2_ID"]].rename(columns={"TEAM2_ID": "TEAM_ID"})
    ])

    played = (
        all_matches.groupby("TEAM_ID")
        .size()
        .reset_index(name="MATCHES_PLAYED")
    )

    team_stats = played.merge(
        wins[["TEAM_ID", "WINS"]],
        on="TEAM_ID",
        how="left"
    )

    team_stats["WINS"] = team_stats["WINS"].fillna(0)

    team_stats["WIN_PERCENTAGE"] = (
        team_stats["WINS"] / team_stats["MATCHES_PLAYED"] * 100
    ).round(2)

    team_stats = team_stats.merge(
        teams,
        on="TEAM_ID",
        how="left"
    )

    fig5 = px.bar(
        team_stats.sort_values("WIN_PERCENTAGE"),
        x="WIN_PERCENTAGE",
        y="TEAM_NAME",
        orientation="h",
        title="Team Win Percentage",
        text="WIN_PERCENTAGE"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # -------------------------
    # 6. PLAYER COMPARISON
    # -------------------------

    st.subheader("6. Compare Player Performance")

    player_names = sorted(
        players["PLAYER_NAME"].dropna().unique()
    )

    selected_players = st.multiselect(
        "Select Players to Compare",
        player_names,
        default=player_names[:2]
    )

    comparison = players[
        players["PLAYER_NAME"].isin(selected_players)
    ]

    if not comparison.empty:

        fig6 = px.bar(
            comparison,
            x="PLAYER_NAME",
            y=["TOTAL_RUNS", "TOTAL_WICKETS"],
            barmode="group",
            title="Player Performance Comparison"
        )

        st.plotly_chart(fig6, use_container_width=True)

    else:
        st.info("Select players to compare.")

except Exception as e:
    st.error(f"Analytics error: {e}")

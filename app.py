
import streamlit as st
import oracledb
import pandas as pd
import plotly.express as px
import os

from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="IPL Analytics",
    page_icon="🏏",
    layout="wide"
)

# -------------------------------
# DATABASE CONNECTION
# -------------------------------

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


def fetch_data(cursor, query):

    cursor.execute(query)

    columns = [col[0] for col in cursor.description]

    return pd.DataFrame(
        cursor.fetchall(),
        columns=columns
    )


# -------------------------------
# DASHBOARD DESIGN
# -------------------------------

st.title("🏏 IPL ANALYTICS")
st.caption("Indian Premier League | Performance & Statistics")

st.divider()

try:

    conn = get_connection()
    cursor = conn.cursor()

    # TOTAL MATCHES
    cursor.execute(
        "SELECT COUNT(*) FROM MATCHES"
    )
    total_matches = cursor.fetchone()[0]

    # TOTAL PLAYERS
    cursor.execute(
        "SELECT COUNT(*) FROM PLAYERS"
    )
    total_players = cursor.fetchone()[0]

    # TOTAL TEAMS
    cursor.execute(
        "SELECT COUNT(*) FROM TEAMS"
    )
    total_teams = cursor.fetchone()[0]

    # TOTAL SEASONS
    cursor.execute(
        "SELECT COUNT(DISTINCT SEASON) FROM MATCHES"
    )
    total_seasons = cursor.fetchone()[0]

    # -------------------------------
    # KPI CARDS
    # -------------------------------

    st.subheader("League Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Matches", total_matches)
    c2.metric("Total Players", total_players)
    c3.metric("Total Teams", total_teams)
    c4.metric("Total Seasons", total_seasons)

    st.divider()

    # -------------------------------
    # TOP RUN SCORERS
    # -------------------------------

    st.subheader("🏆 Top Run Scorers")

    runs_query = """
        SELECT
            P.PLAYER_NAME,
            SUM(S.RUNS) AS TOTAL_RUNS
        FROM PLAYERS P
        JOIN PLAYER_MATCH_STATS S
        ON P.PLAYER_ID = S.PLAYER_ID
        GROUP BY P.PLAYER_ID, P.PLAYER_NAME
        ORDER BY TOTAL_RUNS DESC
    """

    runs_df = fetch_data(cursor, runs_query)

    runs_df = runs_df.head(10)

    fig_runs = px.bar(
        runs_df,
        x="TOTAL_RUNS",
        y="PLAYER_NAME",
        orientation="h",
        title="Top 10 Run Scorers",
        color="TOTAL_RUNS",
        text="TOTAL_RUNS"
    )

    fig_runs.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_runs, use_container_width=True)

    st.divider()

    # -------------------------------
    # TOP WICKET TAKERS
    # -------------------------------

    st.subheader("🎯 Top Wicket Takers")

    wickets_query = """
        SELECT
            P.PLAYER_NAME,
            SUM(S.WICKETS) AS TOTAL_WICKETS
        FROM PLAYERS P
        JOIN PLAYER_MATCH_STATS S
        ON P.PLAYER_ID = S.PLAYER_ID
        GROUP BY P.PLAYER_ID, P.PLAYER_NAME
        ORDER BY TOTAL_WICKETS DESC
    """

    wickets_df = fetch_data(cursor, wickets_query)

    wickets_df = wickets_df.head(10)

    fig_wickets = px.bar(
        wickets_df,
        x="TOTAL_WICKETS",
        y="PLAYER_NAME",
        orientation="h",
        title="Top 10 Wicket Takers",
        color="TOTAL_WICKETS",
        text="TOTAL_WICKETS"
    )

    fig_wickets.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_wickets, use_container_width=True)

    st.divider()

    # -------------------------------
    # MATCHES BY SEASON
    # -------------------------------

    st.subheader("📊 Matches by Season")

    season_query = """
        SELECT
            SEASON,
            COUNT(*) AS MATCH_COUNT
        FROM MATCHES
        GROUP BY SEASON
        ORDER BY SEASON
    """

    season_df = fetch_data(cursor, season_query)

    fig_seasons = px.line(
        season_df,
        x="SEASON",
        y="MATCH_COUNT",
        markers=True,
        title="IPL Matches Across Seasons"
    )

    st.plotly_chart(
        fig_seasons,
        use_container_width=True
    )

    cursor.close()
    conn.close()

    st.success("Live data successfully retrieved from Oracle!")

except Exception as e:

    st.error(f"Database Error: {e}")


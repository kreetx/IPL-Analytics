
import streamlit as st
import oracledb
import pandas as pd
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="IPL Teams",
    page_icon="🏆",
    layout="wide"
)

# DATABASE CONNECTION
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


st.title("🏆 IPL Teams Analytics")
st.caption("Explore team records and performance")

try:
    conn = get_connection()

    # TEAM PERFORMANCE
    query = """
        SELECT
            T.TEAM_ID,
            T.TEAM_NAME,
            COUNT(M.MATCH_ID) AS MATCHES_PLAYED,
            SUM(
                CASE WHEN M.WINNER_TEAM_ID = T.TEAM_ID
                THEN 1 ELSE 0 END
            ) AS MATCHES_WON
        FROM TEAMS T
        LEFT JOIN MATCHES M
        ON T.TEAM_ID = M.TEAM1_ID
        OR T.TEAM_ID = M.TEAM2_ID
        GROUP BY T.TEAM_ID, T.TEAM_NAME
        ORDER BY MATCHES_WON DESC
    """

    df = pd.read_sql(query, conn)

    # Calculate losses and win percentage
    df["MATCHES_LOST"] = (
        df["MATCHES_PLAYED"] - df["MATCHES_WON"]
    )

    df["WIN_PERCENTAGE"] = (
        df["MATCHES_WON"] /
        df["MATCHES_PLAYED"] * 100
    ).fillna(0).round(2)

    st.divider()

    # TEAM SELECTION
    st.subheader("Select a Team")

    selected_team = st.selectbox(
        "Choose IPL Team",
        df["TEAM_NAME"].tolist()
    )

    team = df[df["TEAM_NAME"] == selected_team].iloc[0]

    st.header(selected_team)

    # TEAM METRICS
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Matches Played", int(team["MATCHES_PLAYED"]))
    c2.metric("Matches Won", int(team["MATCHES_WON"]))
    c3.metric("Matches Lost", int(team["MATCHES_LOST"]))
    c4.metric("Win Percentage", f'{team["WIN_PERCENTAGE"]}%')

    st.divider()

    # TEAM COMPARISON
    st.subheader("📊 Team Performance Comparison")

    fig = px.bar(
        df.sort_values("MATCHES_WON"),
        x="MATCHES_WON",
        y="TEAM_NAME",
        orientation="h",
        color="WIN_PERCENTAGE",
        text="MATCHES_WON",
        title="Total Wins by IPL Teams"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # SEASON-WISE PERFORMANCE
    st.subheader("📅 Season-wise Performance")

    season_query = """
        SELECT
            T.TEAM_NAME,
            M.SEASON,
            COUNT(*) AS MATCHES_PLAYED,
            SUM(
                CASE WHEN M.WINNER_TEAM_ID = T.TEAM_ID
                THEN 1 ELSE 0 END
            ) AS MATCHES_WON
        FROM TEAMS T
        JOIN MATCHES M
        ON T.TEAM_ID = M.TEAM1_ID
        OR T.TEAM_ID = M.TEAM2_ID
        GROUP BY T.TEAM_NAME, M.SEASON
        ORDER BY M.SEASON
    """

    season_df = pd.read_sql(season_query, conn)

    filtered = season_df[
        season_df["TEAM_NAME"] == selected_team
    ]

    fig2 = px.line(
        filtered,
        x="SEASON",
        y="MATCHES_WON",
        markers=True,
        title=f"{selected_team} - Season-wise Wins"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # COMPLETE TEAM TABLE
    st.subheader("All Team Statistics")

    st.dataframe(
        df[[
            "TEAM_NAME",
            "MATCHES_PLAYED",
            "MATCHES_WON",
            "MATCHES_LOST",
            "WIN_PERCENTAGE"
        ]],
        use_container_width=True,
        hide_index=True
    )

    conn.close()

    st.success("Team statistics loaded successfully!")

except Exception as e:
    st.error(f"Database Error: {e}")

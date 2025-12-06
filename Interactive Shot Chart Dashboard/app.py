import streamlit as st
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import plotly.graph_objects as go
import numpy as np

# Functions and Team Logo/Colors
from shot_chart_utils import draw_half_court, calculate_zone_efficiency 
from team_logos import get_team_logo_url, get_team_colors 


# --- 1. CONFIGURATION AND CACHING ---

st.set_page_config(layout="wide", page_title="NBA Shot Chart Dashboard")

@st.cache_data
def get_player_list():
    """Fetches and caches the list of all active NBA players."""
    return sorted([p['full_name'] for p in players.get_players() if p['is_active']])

@st.cache_data(show_spinner="Fetching shot data from NBA API...")
def get_shot_data(player_name, season):
    """Fetches and caches detailed shot data for a selected player and season."""
    
    # 1. Get Player ID
    nba_players = players.get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    if not player_info:
        return pd.DataFrame(), None # Return empty data if not found
        
    player_id = player_info[0]['id']

    # 2. Call the Shot Chart Endpoint
    try:
        shot_chart = shotchartdetail.ShotChartDetail(
            team_id=0,
            player_id=player_id,
            context_measure_simple='FGA',
            season_nullable=season
            
        )
        
        df = shot_chart.get_data_frames()[0]
        
        # Determine the player's team ID for the selected season
        team_id = df['TEAM_ID'].iloc[0] if not df.empty else None

        # Prepare columns for visualization and analysis
        df['SHOT_RESULT'] = df.apply(lambda row: 'Made' if row['SHOT_MADE_FLAG'] == 1 else 'Missed', axis=1)
        
        # Return the DataFrame and Team ID
        return df, team_id
    except Exception as e:
        st.error(f"Error fetching data for {player_name}: {e}")
        return pd.DataFrame(), None


# --- 2. SIDEBAR FOR FILTERS ---

st.sidebar.title("🏀 Player & Season Selection")

player_names = get_player_list()

selected_player = st.sidebar.selectbox(
    'Select Player:',
    player_names,
    # Default Player: Alex Sarr Future GOAT
    index=player_names.index('Alex Sarr') if 'Alex Sarr' in player_names else 0 
)

selected_season = st.sidebar.selectbox(
    'Select Season:',
    ['2025-26', '2024-25', '2023-24', '2022-23', '2021-22', '2020-21', '2019-20'],
    index=0
)

# Fetch the data based on selection
df_shots, team_id = get_shot_data(selected_player, selected_season)

# --- THEME CUSTOMIZATION ---
primary_color, secondary_color = get_team_colors(team_id)

st.markdown(
    f"""
    <style>
        /* Change the main background color */
        .stApp {{
            background-color: {primary_color};
            color: {secondary_color}; 
        }}
        /* Change header colors to secondary color */
        h1, h2, h3, h4, .css-10trblm {{
            color: {secondary_color};
        }}
        /* Change sidebar background color */
        .css-1d3z3vf {{
            background-color: {primary_color}; 
        }}
        /* Ensure the data table uses a readable color */
        .stDataFrame div[data-testid="stDataFrame"] {{
             color: black !important; 
        }}
    </style>
    """,
    unsafe_allow_html=True,
)
# ---------------------------

# --- 3. MAIN DASHBOARD LAYOUT ---

# --- LOGO & TITLE SECTION ---
logo_url = get_team_logo_url(team_id)

# Use columns for layout: [Title/Subheader] | [Logo]
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.title(f"🔥 {selected_player} Shot Chart Analysis")
    st.subheader(f"{selected_season} Season")

with col_logo:
    if logo_url:
        st.image(logo_url, width=100)
    elif df_shots is not None and not df_shots.empty:
        st.warning("No logo available.")
# -----------------------------


if df_shots is None or df_shots.empty:
    st.warning("No shot data available for the selected criteria.")
else:
    # --- TABS: CHART vs. EFFICIENCY TABLE ---
    tab1, tab2 = st.tabs(["📊 Interactive Shot Chart", "📈 Efficiency Report"])

    with tab1:
        st.header("Shot Location & Efficiency")
        
        # Base Court Figure
        fig = draw_half_court(title=f"Shot Chart for {selected_player}")

        # Plot Shots
        fig.add_trace(go.Scatter(
            x=df_shots['LOC_X'], 
            y=df_shots['LOC_Y'], 
            mode='markers',
            marker=dict(
                # Green for made, Red for missed
                color=df_shots['SHOT_RESULT'].map({'Made': 'lightgreen', 'Missed': 'red'}),
                size=8,
                opacity=0.7,
                line=dict(width=1, color='rgba(0,0,0,0.5)')
            ),
            # Interactive hover text
            hovertemplate=
                '<b>Result:</b> %{customdata[0]}<br>' +
                '<b>Type:</b> %{customdata[1]}<br>' +
                '<b>Distance:</b> %{customdata[2]} ft<br>' +
                '<extra></extra>', # Removes the default trace name
            customdata=df_shots[['SHOT_RESULT', 'ACTION_TYPE', 'SHOT_DISTANCE']]
        ))
        
        # Display the figure
        st.plotly_chart(fig, width='stretch')
        
    with tab2:
        st.header("Zone Efficiency Breakdown")
        
        # Calculate the zone stats using the utility function
        df_efficiency = calculate_zone_efficiency(df_shots)
        
        # Formatted Column
        df_efficiency['FG_PCT'] = (df_efficiency['FG_PCT'] * 100).round(1).astype(str) + '%'
        
        # Column Renaming for Clarity
        df_efficiency.columns = ['Zone Name', 'Attempts (FGA)', 'Made (FGM)', 'FG Percentage']
        
        # Display the efficiency table
        st.dataframe(df_efficiency, width='stretch', hide_index=True)
        
        st.markdown(f"***\nTotal shots analyzed: **{len(df_shots)}**")
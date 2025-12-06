import streamlit as st
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail, commonplayerinfo
import plotly.graph_objects as go
import numpy as np

# Functions and Team Logo/Colors
from shot_chart_utils import draw_half_court, calculate_zone_efficiency 
from team_logos import get_team_logo_url, get_team_colors 


# --- 1. CONFIGURATION AND CACHING ---

def get_player_headshot_url(player_name):
    #Player headshot URL
    nba_players = players.get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    
    if not player_info:
        return None
    
    player_id = player_info[0]['id']

    return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

st.set_page_config(layout="wide", page_title="NBA Shot Chart Dashboard")

@st.cache_data
def get_player_list():
    #Active NBA player list
    return sorted([p['full_name'] for p in players.get_players() if p['is_active']])

def get_player_position(player_name):
    #Player position retrieval
    nba_players = players.get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    
    if not player_info:
        return None
    
    player_id = player_info[0]['id']
    
    try:
        player_details = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        player_data = player_details.get_normalized_dict()
        position = player_data['CommonPlayerInfo'][0]['POSITION']
        return position
    except Exception as e:
        print(f"Error fetching position for {player_name}: {e}")
        return None

@st.cache_data(show_spinner="Fetching shot data from NBA API...", ttl=21600)
def get_shot_data(player_name, season):
    #Shot chart data retrieval    
    nba_players = players.get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    if not player_info:
        return pd.DataFrame(), None # Return empty data if not found
        
    player_id = player_info[0]['id']

    # Shot chart data fetch
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
    


@st.cache_data(show_spinner="Fetching career stats...", ttl=21600)
def get_career_stats(player_name):
    #Career per-game averages broken down by season
    
    # 1. Get Player ID
    nba_players = players.get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    if not player_info:
        return pd.DataFrame() 
        
    player_id = player_info[0]['id']



    try:
        from nba_api.stats.endpoints import playercareerstats
        
        career_stats = playercareerstats.PlayerCareerStats(
            player_id=player_id,
            per_mode36='PerGame' 
        )
        
        # Regular season averages
        df_season_averages = career_stats.get_data_frames()[0].sort_values(by='SEASON_ID', ascending=False)     
        
        
        # Drop irrelevant columns 
        df_season_averages = df_season_averages.drop(columns=['PLAYER_ID', 'LEAGUE_ID'])
        
        return df_season_averages
    except Exception as e:
        st.error(f"Error fetching career data: {e}")
        return pd.DataFrame()


# --- 2. SIDEBAR FOR FILTERS ---

st.sidebar.title("🏀 Player & Season Selection")

player_names = get_player_list()

selected_player = st.sidebar.selectbox(
    'Select Player:',
    player_names,
    # Default Player: Alex Sarr future GOAT
    index=player_names.index('Alex Sarr') if 'Alex Sarr' in player_names else 0 
)

selected_season = st.sidebar.selectbox(
    'Select Season:',
    ['2025-26', '2024-25', '2023-24', '2022-23', '2021-22', '2020-21', '2019-20'],
    index=0
)

# Fetch the data based on selection
df_shots, team_id = get_shot_data(selected_player, selected_season)

df_career_totals = get_career_stats(selected_player)

player_position = get_player_position(selected_player) 

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
headshot_url = get_player_headshot_url(selected_player)

# Use columns for layout: [Headshot] | [Title/Subheader] | [Logo]
col_headshot, col_title, col_logo = st.columns([1, 5, 1])

with col_headshot:
    if headshot_url:
        st.markdown(
            f"""
            <img src="{headshot_url}" style="width: 180px; height: 120px; object-fit: cover;">
            """,
            unsafe_allow_html=True
        )

with col_title:
    # 1. Highest Priority: Player Name
    st.title(f"{selected_player} - {player_position}")
    
    # 2. Secondary Priority: Season
    st.subheader(f"{selected_season} Season") 

with col_logo:
    if logo_url:
        st.image(logo_url, width=100)
    elif df_shots is not None and not df_shots.empty:
        st.warning("No logo available.")
# -----------------------------
# --- STATS METRIC DISPLAY  ---
if not df_career_totals.empty:
    # Filter to get stats for the currently selected season
    current_season_stats = df_career_totals[df_career_totals['SEASON_ID'] == selected_season]
    
    if not current_season_stats.empty:
        stats = current_season_stats.iloc[0]
        
        # Calculate and format the five key stats
        ppg = stats['PTS'].round(1)
        rpg = stats['REB'].round(1)
        apg = stats['AST'].round(1)
        fg_pct = (stats['FG_PCT'] * 100).round(1)
        fg3_pct = (stats['FG3_PCT'] * 100).round(1)

        # Use custom HTML hr with zero margin
        st.markdown('<hr style="margin: 0.5rem 0 0.5rem 0;">', unsafe_allow_html=True) 
        
        # Define the font size style for the metrics (e.g., 28px)
        metric_style = 'font-size: 28px; font-weight: bold;'
        
        # Display the metrics in five equal columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Use HTML span with custom size/style for values
        with col1:
            st.markdown("###### PTS")
            st.markdown(f'<span style="{metric_style}">{ppg}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown("###### REB")
            st.markdown(f'<span style="{metric_style}">{rpg}</span>', unsafe_allow_html=True)
        with col3:
            st.markdown("###### AST")
            st.markdown(f'<span style="{metric_style}">{apg}</span>', unsafe_allow_html=True)
        with col4:
            st.markdown("###### FG%")
            st.markdown(f'<span style="{metric_style}">{fg_pct}%</span>', unsafe_allow_html=True)
        with col5:
            st.markdown("###### 3P%")
            st.markdown(f'<span style="{metric_style}">{fg3_pct}%</span>', unsafe_allow_html=True)
        
        st.markdown('<hr style="margin: 0.5rem 0 0.5rem 0;">', unsafe_allow_html=True)

if df_shots is None or df_shots.empty:
    st.warning("No shot data available for the selected criteria.")
else:
    # --- TABS: CHART vs. EFFICIENCY TABLE ---
    tab1, tab2, tab3 = st.tabs(["📊 Interactive Shot Chart", "📈 Efficiency Report", "⭐ Career Averages"])

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
    

    with tab3:
        st.header(f"Career Regular Season Averages by Season ({selected_player})")
        
        if df_career_totals.empty:
            st.warning("Career statistics are not available for this player.")
        else:
            # 1. Define the columns to keep using the original API names
            columns_to_keep = [
                'SEASON_ID', 
                'TEAM_ABBREVIATION', 
                'GP', 
                'MIN', 
                'PTS', 
                'REB', 
                'AST', 
                'STL', 
                'BLK', 
                'TOV',
                'FG_PCT', 
                'FT_PCT', 
                'FG3_PCT'
            ]

            # 2. Setting Display DataFrame
            df_display = df_career_totals[columns_to_keep]
            
            # 3. Column Rename
            df_display = df_display.rename(columns={
                'SEASON_ID': 'Season',
                'TEAM_ABBREVIATION': 'Team',
                'FG_PCT': 'FG%',
                'FT_PCT': 'FT%',
                'FG3_PCT': '3P%'
            })
            
            st.dataframe(
                df_display, 
                width='stretch', 
                hide_index=True
            )
import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail, commonplayerinfo, playergamelog
from shot_chart_utils import calculate_zone_efficiency
import pandas as pd

@st.cache_data(ttl=604800)
def get_players():
    #Fetch NBA players
    return players.get_players()

@st.cache_data
def get_player_headshot_url(player_name):
    #Player headshot URL
    nba_players = get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    
    if not player_info:
        return None
    
    player_id = player_info[0]['id']

    return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

@st.cache_data(ttl=604800)
def get_player_list():
    #Active NBA player list
    return sorted([p['full_name'] for p in get_players() if p['is_active']])

@st.cache_data(ttl=604800)
def get_player_position(player_name):
    #Player position retrieval
    nba_players = get_players()
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
    nba_players = get_players()
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

        #copy dataframe to prevent in-place modification issues
        df = df.copy()
        
        # Determine the player's team ID for the selected season
        team_id = df['TEAM_ID'].iloc[0] if not df.empty else None


        # Prepare columns for visualization and analysis
        df['SHOT_RESULT'] = df.apply(lambda row: 'Made' if row['SHOT_MADE_FLAG'] == 1 else 'Missed', axis=1)
        
        # Return the DataFrame and Team ID
        return df, team_id
    except Exception as e:
        st.error(f"Error fetching data for {player_name}: {e}")
        return pd.DataFrame(), None

@st.cache_data
def get_zone_efficiency_cached(player_name, season, df):
    return calculate_zone_efficiency(df)



@st.cache_data(show_spinner="Fetching career stats...", ttl=21600)
def get_career_stats(player_name):
    #Career per-game averages broken down by season
    
    # 1. Get Player ID
    nba_players = get_players()
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
    

#Game Log
@st.cache_data(show_spinner="Fetching game log data...", ttl=21600)
def get_player_game_log(player_name, season):
    #Fetch player's game log for a specific season
    
    # 1. Get Player ID
    nba_players = get_players()
    player_info = [p for p in nba_players if p['full_name'] == player_name]
    if not player_info:
        return pd.DataFrame() 
        
    player_id = player_info[0]['id']
    
    try:
        game_log = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star='Regular Season'
        )
        
        df_game_log = game_log.get_data_frames()[0]
        
        return df_game_log
    except Exception as e:
        st.error(f"Error fetching game log data: {e}")
        return pd.DataFrame()
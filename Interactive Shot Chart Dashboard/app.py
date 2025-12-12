import streamlit as st
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail, commonplayerinfo
import plotly.graph_objects as go
import numpy as np
from cache_utils import get_player_headshot_url, get_player_list, get_player_position, get_shot_data, get_career_stats, get_zone_efficiency_cached, get_player_game_log


# Functions and Team Logo/Colors
from shot_chart_utils import draw_half_court, calculate_zone_efficiency 
from team_logos import get_team_logo_url, get_team_colors 


# --- 1. CONFIGURATION---

st.set_page_config(layout="wide", page_title="NBA Shot Chart Dashboard")

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

game_log = get_player_game_log(selected_player, selected_season)





# --- THEME CUSTOMIZATION ---

primary_color, secondary_color = get_team_colors(team_id)

st.markdown(
    f"""
    <style>
        /* Change the main background color */
        .stApp {{
            background-color: {primary_color};
            color: #FFFFFF; 
        }}
        /* Change header colors to secondary color */
        h1, h2, h3, h4, .css-10trblm {{
            color: #FFFFFF;
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
    # We use HTML here to force the Secondary Color ONLY for this title
    st.markdown(f"""
        <h1 style='color: {secondary_color}; margin-bottom: 0px;'>{selected_player} - {player_position}</h1>
        <h3 style='color: {secondary_color}; margin-top: 0px;'>{selected_season} Season</h3>
    """, unsafe_allow_html=True)

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Scouting Report", "📊 Interactive Shot Chart", "📈 Efficiency Report", "⭐ Career Averages", "📅 Regular Season Game Log"])

    with tab2:
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
        
    with tab3:
        st.header("Zone Efficiency Breakdown")
        
        # Calculate the zone stats using the utility function
        df_efficiency = get_zone_efficiency_cached(selected_player, selected_season, df_shots)
        
        #Formatted column 
        df_efficiency['FG_PCT'] = df_efficiency['FG_PCT'] * 100.0

        
        # Column Renaming for Clarity
        df_efficiency.columns = ['Zone Name', 
                                 'Attempts (FGA)', 
                                 'Made (FGM)', 
                                 'FG Percentage']

        

        df_efficiency = df_efficiency.sort_values(by='FG Percentage', ascending=False)
        
        # Display the efficiency table
        st.dataframe(
        df_efficiency[['Zone Name', 'Made (FGM)', 'Attempts (FGA)', 'FG Percentage']], 
        width='stretch', 
        hide_index=True,
        column_config={
            
            "FG Percentage": st.column_config.ProgressColumn(
                "FG Percentage",
                help="Field Goal Efficiency by Zone",
                
                # Formatting to display as percentage
                format="%.1f%%", 
                
                min_value=0.0, 
                max_value=100.0
            )
        }
    )      
        st.markdown(f"***\nTotal shots analyzed: **{len(df_shots)}**")
    

    with tab4:
        st.header(f"Career Regular Season Averages by Season")
        
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

    with tab5:


        st.header(f"Game Log for {selected_season} Regular Season")
        
        if game_log is None or game_log.empty:
            st.warning("Game log data is not available for this player/season.")
        else:
            columns_to_keep = [
                'GAME_DATE', 
                'MATCHUP', 
                'WL', 
                'MIN', 
                'FGM',
                'FGA',
                'FG_PCT',
                'FG3M',
                'FG3A',
                'FG3_PCT',
                'FTM',
                'FTA',
                'FT_PCT',
                'OREB',
                'DREB',
                'PTS', 
                'REB', 
                'AST', 
                'STL', 
                'BLK', 
                'TOV',
                'PF',
                'PLUS_MINUS'
            ]

            df_display = game_log[columns_to_keep]

            df_display = df_display.rename(columns={
                'GAME_DATE': 'Date',
                'WL': 'W/L',
                'FGM': 'FG Made',
                'FGA': 'FG Attempted',
                'FG_PCT': 'FG%',
                'FG3M': '3P Made',
                'FG3A': '3P Attempted',
                'FG3_PCT': '3P%',
                'FTM': 'FT Made',
                'FTA': 'FT Attempted',
                'FT_PCT': 'FT%',
                'OREB': 'Off Reb',
                'DREB': 'Def Reb',
                'PF': 'Personal Fouls',
                'PLUS_MINUS': '+/-'
            })

            #for col in ['FG%', '3P%', 'FT%']:
            #    df_display[col] = (df_display[col] * 100).round(1).astype(str) + '%'



            st.dataframe(
                df_display,
                width='stretch',
                hide_index=True,
                column_config={
                "GAME_DATE": st.column_config.DatetimeColumn("Date", format="MMM DD, YYYY")
                }
            )

    with tab1:
        st.header("📋 Scouting Report")
        st.markdown("*> Generated based on spatial data and game logs.*")

        if df_shots.empty or game_log.empty:
            st.warning("Insufficient data to generate analysis.")
        else:
            # A. OFFENSIVE AUDIT LOGIC
            zone_stats = df_shots.groupby(['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA']).apply(
                lambda x: pd.Series({
                    'FGA': len(x),
                    'FGM': x['SHOT_MADE_FLAG'].sum(),
                    'FG_PCT': x['SHOT_MADE_FLAG'].mean()
                })
            ).reset_index()
            
            # Create combined name like in your efficiency table
            zone_stats['ZONE_NAME'] = zone_stats['SHOT_ZONE_BASIC'] + ' - ' + zone_stats['SHOT_ZONE_AREA']
            
            # Filter for zones with at least 5 attempts 
            qualified_zones = zone_stats[zone_stats['FGA'] > 5].copy()
            
            if not qualified_zones.empty:
                # Sort by FG% first (descending), then by FGA (descending) for tiebreaker
                qualified_zones_sorted_best = qualified_zones.sort_values(
                    by=['FG_PCT', 'FGA'], 
                    ascending=[False, False]
                )
                
                # Sort by FG% first (ascending), then by FGA (descending) for worst
                qualified_zones_sorted_worst = qualified_zones.sort_values(
                    by=['FG_PCT', 'FGA'], 
                    ascending=[True, False]
                )
                
                # Get top 3
                top_3_best = qualified_zones_sorted_best.head(3)
                top_3_worst = qualified_zones_sorted_worst.head(3)
            else:
                top_3_best = pd.DataFrame()
                top_3_worst = pd.DataFrame()

            # B. DEFENSIVE SCOUTING LOGIC (Left vs Right Splits)
            # LOC_X < 0 is Left Side (Stage Left/Court Right), LOC_X > 0 is Right Side
            left_side = df_shots[df_shots['LOC_X'] < 0].copy()
            right_side = df_shots[df_shots['LOC_X'] > 0].copy()
            
            # Add minimum sample size
            min_attempts = 10
            if len(left_side) >= min_attempts and len(right_side) >= min_attempts:
                left_pct = left_side['SHOT_MADE_FLAG'].mean()
                right_pct = right_side['SHOT_MADE_FLAG'].mean()
                
                # Determine strong hand
                if left_pct > (right_pct + 0.05):
                    hand_bias = "LEFT"
                    defensive_strategy = "FORCE RIGHT"
                elif right_pct > (left_pct + 0.05):
                    hand_bias = "RIGHT"
                    defensive_strategy = "FORCE LEFT"
                else:
                    hand_bias = "BALANCED"
                    defensive_strategy = "PLAY STRAIGHT UP"
            else:
                hand_bias = "INSUFFICIENT DATA"
                defensive_strategy = "NEED MORE SHOT VOLUME"
                left_pct = right_pct = 0
            
            # C. RELIABILITY LOGIC (Consistency)
            if not game_log.empty and len(game_log) > 1:
                avg_pts = game_log['PTS'].mean()
                std_dev_pts = game_log['PTS'].std()
                
                # Coefficient of Variation (CV) - Lower is more consistent
                cv = std_dev_pts / avg_pts if avg_pts > 0 else 0
                
                if cv < 0.2:
                    consistency_grade = "High Reliability (Consistent)"
                    consistency_description = "This player delivers predictable scoring output game-to-game. Defenses can't rely on off-nights, and offenses can count on steady production."
                elif cv < 0.4:
                    consistency_grade = "Moderate Variance (Normal)"
                    consistency_description = "Standard NBA variability. The player has occasional hot and cold streaks, but performance stays within a reasonable range."
                else:
                    consistency_grade = "High Variance (Volatile)"
                    consistency_description = "Boom-or-bust player. Expect significant swings between dominant performances and quiet nights. Game plan accordingly based on matchups and recent form."
            else:
                consistency_grade = "Insufficient Games Played"
                consistency_description = "Need more game data to assess scoring consistency patterns."
                cv = 0

            # --- UI DISPLAY ---

            # COLUMN 1: OFFENSIVE OPTIMIZATION
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Offensive Optimization")
                if not top_3_best.empty:
                    st.success("**🟢 Green Light Zones** (Highest Value)")
                    st.write("Most efficient zones weighted by volume and shot value:")
                    
                    for idx, zone in top_3_best.iterrows():
                        with st.container():
                            st.markdown(f"**{zone['ZONE_NAME']}**")
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("FG%", f"{zone['FG_PCT']*100:.1f}%")
                            col_b.metric("Makes", f"{int(zone['FGM'])}")
                            col_c.metric("Attempts", f"{int(zone['FGA'])}")
                            st.markdown("---")
                    
                    st.error("**🔴 Red Light Zones** (Lowest Value)")
                    st.write("The player struggles here. Defenses should invite these shots:")
                    
                    for idx, zone in top_3_worst.iterrows():
                        with st.container():
                            st.markdown(f"**{zone['ZONE_NAME']}**")
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("FG%", f"{zone['FG_PCT']*100:.1f}%")
                            col_b.metric("Makes", f"{int(zone['FGM'])}")
                            col_c.metric("Attempts", f"{int(zone['FGA'])}")
                            st.markdown("---")
                else:
                    st.info("Not enough shot attempts per zone (need >5) to generate recommendations.")

            # COLUMN 2: DEFENSIVE SCOUTING
            with col2:
                st.subheader("🛡️ Defensive Strategy")
                
                # --- 1. DIRECTIONAL BIAS ---
                if hand_bias != "INSUFFICIENT DATA":
                    st.info(f"**Directive:** {defensive_strategy}")
                    
                    st.write("### Directional Splits")
                    c1, c2 = st.columns(2)
                    c1.metric("Left Side FG%", f"{left_pct*100:.1f}%")
                    c2.metric("Right Side FG%", f"{right_pct*100:.1f}%")
                    
                    if hand_bias != "BALANCED":
                        st.caption(f"Player shoots significantly better from the **{hand_bias}** side.")
                    else:
                        st.caption("Player is ambidextrous/balanced.")
                else:
                    st.warning("Need at least 10 attempts per side for directional analysis.")
                
                st.markdown("---")
                
                # --- 2. DEFENSIVE COVERAGE SCHEME ---
                st.write("### 🧪 Defensive Coverage Scheme")
                st.caption("Which defensive layer should we concede to minimize expected points?")
                
                # Helper function to categorize shots into defensive layers
                def get_defensive_layer(row):
                    zone = row['SHOT_ZONE_BASIC']
                    if 'Restricted Area' in zone:
                        return 'Rim (Protect)'
                    elif 'Mid-Range' in zone or 'In The Paint (Non-RA)' in zone:
                        return 'Mid-Range (Force)'
                    elif 'Above the Break 3' in zone or 'Corner 3' in zone or 'Backcourt' in zone:
                        return 'Perimeter (Chase)'
                    return 'Other'
                
                # Create distinct copy for layer analysis
                layer_df = df_shots.copy()
                layer_df['DEF_LAYER'] = layer_df.apply(get_defensive_layer, axis=1)
                
                # Calculate PPS (Points Per Shot) by layer
                def calculate_pps(group):
                    total_points = 0
                    for _, shot in group.iterrows():
                        if shot['SHOT_MADE_FLAG'] == 1:
                            # Check actual shot type for correct point value
                            points = 3 if shot['SHOT_TYPE'] == '3PT Field Goal' else 2
                            total_points += points
                    return total_points / len(group) if len(group) > 0 else 0
                
                layer_stats = layer_df.groupby('DEF_LAYER').apply(
                    lambda x: pd.Series({
                        'FGA': len(x),
                        'FG_PCT': x['SHOT_MADE_FLAG'].mean(),
                        'PPS': calculate_pps(x)
                    })
                ).reset_index()
                
                # Filter valid layers with sufficient volume
                layer_stats = layer_stats[layer_stats['DEF_LAYER'] != 'Other']
                layer_stats = layer_stats[layer_stats['FGA'] > 5]
                
                if not layer_stats.empty:
                    # Find lowest and highest PPS layers
                    force_layer = layer_stats.loc[layer_stats['PPS'].idxmin()]
                    deny_layer = layer_stats.loc[layer_stats['PPS'].idxmax()]
                    
                    # Display strategy
                    st.success(f"**✅ FORCE: {force_layer['DEF_LAYER']}**")
                    st.write(f"Concede this layer. It yields the lowest points per possession (**{force_layer['PPS']:.2f} PPS**).")
                    
                    st.error(f"**❌ DENY: {deny_layer['DEF_LAYER']}**")
                    st.write(f"Do not allow attempts here (**{deny_layer['PPS']:.2f} PPS**).")
                    
                    # Visualization
                    st.bar_chart(layer_stats.set_index('DEF_LAYER')['PPS'])
                    st.caption("Points Per Shot (PPS) by Defensive Layer")
                else:
                    st.info("Insufficient volume to determine coverage scheme.")
            
            st.divider()

            # SECTION 3: CONSISTENCY REPORT
            st.subheader("📉 Reliability & Context")
            st.write(f"**Grading:** {consistency_grade}")
            st.write(f"*{consistency_description}*")
            
            if not game_log.empty and len(game_log) > 1:
                # Show key stats
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                col_stat1.metric("Average PPG", f"{avg_pts:.1f}")
                col_stat2.metric("Std Deviation", f"{std_dev_pts:.1f}", 
                            help="Measures game-to-game variation. Lower = more predictable scoring.")
                col_stat3.metric("Coeff. of Variation", f"{cv:.2f}", 
                            help="Consistency metric (Std Dev ÷ Average). Under 0.2 = very consistent, over 0.4 = volatile.")
                
                # Add interpretive context
                st.write(f"**Typical scoring range:** {avg_pts - std_dev_pts:.1f} to {avg_pts + std_dev_pts:.1f} points (~68% of games)")
                
                # Visualization of Variance
                st.bar_chart(game_log.set_index('GAME_DATE')[['PTS']])
                st.caption("Game-by-Game Scoring Output showing variance.")
            else:
                st.info("Need multiple games to assess consistency.")
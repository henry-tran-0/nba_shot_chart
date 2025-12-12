import plotly.graph_objects as go
import numpy as np

def draw_half_court(title="NBA Shot Chart"):
    """
    Creates a Plotly figure with standard NBA half-court markings.
    """
    fig = go.Figure()
    
    # Colors
    court_color = 'black'
    line_color = 'white'
    
    # NBA API coordinates (10 units = 1 foot)
    corner_x = 220.0  # 22 ft
    arc_radius = 237.5 # 23.75 ft
    baseline_y = -47.5
    
    # Calculation: y-coordinate where the 3-point straight line meets the arc
    arc_y = (arc_radius**2 - corner_x**2) ** 0.5 # ~89.4719

    # Topmost point of the arc (0, R)
    arc_top_y = arc_radius # 237.5
    
    
    # --- 1. 3-POINT LINE (Three Separate Shapes) ---
    
    # 1.1 Left Corner Line (Straight)
    fig.add_shape(type="line", x0=-corner_x, y0=baseline_y, x1=-corner_x, y1=arc_y,
                  line=dict(color=line_color, width=2))
    
    # 1.2 Right Corner Line (Straight)
    fig.add_shape(type="line", x0=corner_x, y0=baseline_y, x1=corner_x, y1=arc_y,
                  line=dict(color=line_color, width=2))

    # Arc (using many small line segments)
    theta_start = np.arctan2(arc_y, -corner_x)  # Angle to left corner
    theta_end = np.arctan2(arc_y, corner_x)      # Angle to right corner
    theta = np.linspace(theta_start, theta_end, 100)  # 100 points for smooth arc

    arc_x = arc_radius * np.cos(theta)
    arc_y_points = arc_radius * np.sin(theta)

    fig.add_trace(go.Scatter(
    x=arc_x, 
    y=arc_y_points,
    mode='lines',
    line=dict(color=line_color, width=2),
    showlegend=False,
    hoverinfo='skip'
    ))



    # --- 2. ELIMINATE OUT-OF-BOUNDS ARTIFACTS ---
    
    # Masking everything below the baseline to ensure no lines peek out
    fig.add_shape(type="rect", 
                  x0=-300, y0=-260, # Start far outside the court
                  x1=300, y1=baseline_y, # End exactly at the baseline
                  line=dict(width=0), 
                  fillcolor=court_color, # Black fill
                  opacity=1,
                  layer='above' 
    )
    
    
    # --- 3. KEY/PAINT MARKINGS ---

    # Key/Paint Outer Box (16ft wide, 19ft deep from baseline)
    fig.add_shape(type="rect", x0=-80, y0=baseline_y, x1=80, y1=142.5,
                  line=dict(color=line_color, width=2), fillcolor='rgba(0,0,0,0)')

    # Free Throw Circle (Centered at (0, 142.5), Radius 60)
    fig.add_shape(type="circle", x0=-60, y0=82.5, x1=60, y1=202.5,
                  line=dict(color=line_color, width=2), fillcolor='rgba(0,0,0,0)')
    
    # Restricted Area (Radius 40 units/4 feet from hoop center (0,0))
    fig.add_shape(type="circle", x0=-40, y0=-40, x1=40, y1=40,
                  line=dict(color=line_color, width=2), fillcolor='rgba(0,0,0,0)')

    # --- 4. HOOP AND BACKBOARD ---
    
    # Backboard (approx -7.5 y)
    fig.add_shape(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5,
                  line=dict(color=line_color, width=2))

    # Hoop (0, 0)
    fig.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5,
                  line=dict(color=line_color, width=2), fillcolor='rgba(0,0,0,0)')
    
    # --- 5. COURT BOUNDARIES ---
    
    # Baseline 
    fig.add_shape(type="line", x0=-250, y0=baseline_y, x1=250, y1=baseline_y,
                  line=dict(color=line_color, width=2))
    # Sidelines
    fig.add_shape(type="line", x0=-250, y0=baseline_y, x1=-250, y1=422.5,
                  line=dict(color=line_color, width=2))
    fig.add_shape(type="line", x0=250, y0=baseline_y, x1=250, y1=422.5,
                  line=dict(color=line_color, width=2))

    # Layout Configuration 
    fig.update_layout(
        title={'text': title, 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        plot_bgcolor=court_color,
        paper_bgcolor=court_color,
        font_color='white',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-260, 260]),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            visible=False, 
            range=[-60, 430],
            scaleanchor="x", 
            scaleratio=1 
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=600
    )
    
    return fig

def calculate_zone_efficiency(df):
    """
    Calculates FG% for each zone using the existing NBA API columns.
    """
    if df.empty:
        return df

    # Group by the primary zone descriptors
    zone_stats = df.groupby(['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA']).agg(
        FGA=('SHOT_ATTEMPTED_FLAG', 'sum'),
        FGM=('SHOT_MADE_FLAG', 'sum')
    ).reset_index()
    
    # Field Goal Percentage
    zone_stats['FG_PCT'] = np.where(
        zone_stats['FGA'] > 0,
        zone_stats['FGM'] / zone_stats['FGA'],
        0
    )
    
    # Cleaner combined zone name for the table
    zone_stats['ZONE_NAME'] = zone_stats['SHOT_ZONE_BASIC'] + ' - ' + zone_stats['SHOT_ZONE_AREA']
    
    return zone_stats[['ZONE_NAME', 'FGA', 'FGM', 'FG_PCT']]
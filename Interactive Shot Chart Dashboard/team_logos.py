# team_logos.py

TEAM_LOGO_MAP = {
    1610612737: "https://cdn.nba.com/logos/nba/1610612737/global/L/logo.svg", # Atlanta Hawks
    1610612738: "https://cdn.nba.com/logos/nba/1610612738/global/L/logo.svg", # Boston Celtics
    1610612751: "https://cdn.nba.com/logos/nba/1610612751/global/L/logo.svg", # Brooklyn Nets
    1610612766: "https://cdn.nba.com/logos/nba/1610612766/global/L/logo.svg", # Charlotte Hornets
    1610612741: "https://cdn.nba.com/logos/nba/1610612741/global/L/logo.svg", # Chicago Bulls
    1610612739: "https://cdn.nba.com/logos/nba/1610612739/global/L/logo.svg", # Cleveland Cavaliers
    1610612765: "https://cdn.nba.com/logos/nba/1610612765/global/L/logo.svg", # Detroit Pistons
    1610612740: "https://cdn.nba.com/logos/nba/1610612748/global/L/logo.svg", # Miami Heat (Fixing Legacy ID to point to correct logo)
    1610612748: "https://cdn.nba.com/logos/nba/1610612748/global/L/logo.svg", # Miami Heat (Current Primary ID)
    1610612749: "https://cdn.nba.com/logos/nba/1610612749/global/L/logo.svg", # Milwaukee Bucks
    1610612752: "https://cdn.nba.com/logos/nba/1610612752/global/L/logo.svg", # New York Knicks
    1610612753: "https://cdn.nba.com/logos/nba/1610612753/global/L/logo.svg", # Orlando Magic
    1610612755: "https://cdn.nba.com/logos/nba/1610612755/global/L/logo.svg", # Philadelphia 76ers
    1610612761: "https://cdn.nba.com/logos/nba/1610612761/global/L/logo.svg", # Toronto Raptors
    1610612764: "https://cdn.nba.com/logos/nba/1610612764/global/L/logo.svg", # Washington Wizards
    1610612754: "https://cdn.nba.com/logos/nba/1610612754/global/L/logo.svg", # Indiana Pacers
    1610612742: "https://cdn.nba.com/logos/nba/1610612742/global/L/logo.svg", # Dallas Mavericks 
    1610612746: "https://cdn.nba.com/logos/nba/1610612746/global/L/logo.svg", # LA Clippers
    1610612747: "https://cdn.nba.com/logos/nba/1610612747/global/L/logo.svg", # Los Angeles Lakers
    1610612763: "https://cdn.nba.com/logos/nba/1610612763/global/L/logo.svg", # Memphis Grizzlies
    1610612750: "https://cdn.nba.com/logos/nba/1610612750/global/L/logo.svg", # Minnesota Timberwolves
    1610612758: "https://cdn.nba.com/logos/nba/1610612758/global/L/logo.svg", # Sacramento Kings
    1610612759: "https://cdn.nba.com/logos/nba/1610612759/global/L/logo.svg", # San Antonio Spurs
    1610612744: "https://cdn.nba.com/logos/nba/1610612744/global/L/logo.svg", # Golden State Warriors
    1610612745: "https://cdn.nba.com/logos/nba/1610612745/global/L/logo.svg", # Houston Rockets
    1610612756: "https://cdn.nba.com/logos/nba/1610612756/global/L/logo.svg", # Phoenix Suns
    1610612757: "https://cdn.nba.com/logos/nba/1610612757/global/L/logo.svg", # Portland Trail Blazers
    1610612760: "https://cdn.nba.com/logos/nba/1610612760/global/L/logo.svg", # Oklahoma City Thunder
    1610612762: "https://cdn.nba.com/logos/nba/1610612762/global/L/logo.svg", # Utah Jazz
    1610612743: "https://cdn.nba.com/logos/nba/1610612743/global/L/logo.svg", # Denver Nuggets
    1610612740: "https://cdn.nba.com/logos/nba/1610612740/global/L/logo.svg", # New Orleans Pelicans 
    1610612736: "https://cdn.nba.com/logos/nba/1610612740/global/L/logo.svg", # New Orleans Pelicans (Legacy ID)
}

TEAM_COLOR_MAP = {
    # Team ID: (Primary Color - for background, Secondary Color - for accents/text)
    
    1610612737: ("#E03A3E", "#C1D32F"),  # Atlanta Hawks: Red, Yellow/Green
    1610612738: ("#007A33", "#BA9653"),  # Boston Celtics: Green, Gold
    1610612751: ("#000000", "#FFFFFF"),  # Brooklyn Nets: Black, White
    1610612766: ("#1D1160", "#007A87"),  # Charlotte Hornets: Purple, Teal
    1610612741: ("#CE1141", "#000000"),  # Chicago Bulls: Red, Black
    1610612739: ("#6F2E37", "#FDBB30"),  # Cleveland Cavaliers: Wine, Gold
    1610612754: ("#002D62", "#FDBB30"),  # Indiana Pacers: Blue, Gold
    1610612740: ("#98002E", "#F9A01B"),  # Miami Heat: Red/Maroon, Orange
    1610612749: ("#00471B", "#EEE1C6"),  # Milwaukee Bucks: Green, Cream
    1610612752: ("#006BB6", "#F58426"),  # New York Knicks: Blue, Orange
    1610612753: ("#0077C0", "#C4CED4"),  # Orlando Magic: Blue, Silver
    1610612755: ("#006BB6", "#ED174B"),  # Philadelphia 76ers: Blue, Red
    1610612745: ("#000000", "#CE1141"),  # Toronto Raptors (Using current colors/ID)
    1610612764: ("#002B5C", "#E31837"),  # Washington Wizards: Blue, Red
    1610612743: ("#0E2240", "#FEC524"),  # Denver Nuggets: Navy/Blue, Gold
    1610612742: ("#00538C", "#B8C4CA"),  # Dallas Mavericks: Blue, Silver
    1610612745: ("#000000", "#CE1141"),  # Houston Rockets: Red, Blue
    1610612747: ("#552583", "#FDB927"),  # Los Angeles Lakers: Purple, Gold
    1610612746: ("#1D428A", "#C8102E"),  # LA Clippers: Blue, Red
    1610612763: ("#5D76A9", "#121721"),  # Memphis Grizzlies: Blue, Navy
    1610612750: ("#0C2340", "#236192"),  # Minnesota Timberwolves: Navy, Blue
    1610612740: ("#002B5C", "#F9A01B"),  # New Orleans Pelicans : Navy, Gold
    1610612760: ("#007AC1", "#EF3B24"),  # Oklahoma City Thunder: Blue, Orange
    1610612756: ("#1D1160", "#E56020"),  # Phoenix Suns: Purple, Orange
    1610612757: ("#E03A3E", "#000000"),  # Portland Trail Blazers: Red, Black
    1610612758: ("#5A2D81", "#63727A"),  # Sacramento Kings: Purple, Gray
    1610612759: ("#C4CED4", "#000000"),  # San Antonio Spurs: Silver, Black
    1610612762: ("#007A33", "#FDBB30"),  # Utah Jazz: Green, Gold
    1610612744: ("#1D428A", "#FFC72C"),  # Golden State Warriors: Blue, Gold
    1610612765: ("#006BB6", "#ED174B"),  # Detroit Pistons
}


def get_team_colors(team_id):
    """Retrieves the primary and secondary colors based on the team ID."""
    try:
        team_id = int(team_id)
    except (ValueError, TypeError):
        return None, None
        
    # Default to a generic dark theme if ID is missing
    return TEAM_COLOR_MAP.get(team_id, ("#1E1E1E", "#FFFFFF"))

def get_team_logo_url(team_id):
    """
    Retrieves the official NBA logo URL based on the team ID.
    
    Args:
        team_id (int): The NBA team ID (e.g., 1610612743 for DEN).
        
    Returns:
        str: The URL of the team's SVG logo, or None if not found.
    """
    # Cast team_id to int in case the API returns it as a string
    try:
        team_id = int(team_id)
    except (ValueError, TypeError):
        return None
        
    return TEAM_LOGO_MAP.get(team_id, None)

# Note on IDs: Some IDs (like for the Nets, Pelicans, Thunder) 
# have changed over time due to relocation/renaming. The most current IDs are mapped here.
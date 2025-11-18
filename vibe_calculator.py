"""
VIBE - Valued Impact Basketball Estimate

Official VIBE Formula v2.0

A comprehensive basketball metric that combines:
• OVIBE (Offensive Component): TS%, scoring, playmaking, rebounding
• DVIBE (Defensive Component): Steals, blocks, defensive rebounding  
• Impact (Plus-Minus Component): Team performance impact
• Minutes-based shrinkage for statistical stability

Final Formula:
VIBE = 100 + 15 × (0.75×Skill + 0.25×Impact - LeagueMean) / LeagueStd

Where:
- Skill = 0.6×OVIBE + 0.4×DVIBE (z-scores)
- Impact = Plus-minus per 100 possessions (z-score)
- Minutes shrinkage applied for low-minute players

Interpretation:
140+ → MVP-level | 125-140 → All-NBA | 115-125 → Strong starter
100 → League average | <90 → Below-average impact
"""

def calculate_player_possessions(minutes):
    """
    Calculate player possessions using official VIBE formula
    
    PlayerPoss = MIN × 100 / 240
    (240 = 48 minutes × 5 players)
    
    Args:
        minutes (float): Total minutes played
    
    Returns:
        float: Player possessions
    """
    if not minutes or minutes <= 0:
        return 1  # Avoid division by zero
    
    return (minutes * 100) / 240

def calculate_per_100_stats(stats_dict):
    """
    Calculate per-100 possession stats for all relevant metrics
    
    Args:
        stats_dict (dict): Player statistics dictionary
    
    Returns:
        dict: Per-100 possession statistics
    """
    minutes = stats_dict.get('MIN', 0) or 0
    player_poss = calculate_player_possessions(minutes)
    
    if player_poss <= 0:
        return {stat: 0.0 for stat in ['PTS100', 'AST100', 'ORB100', 'DRB100', 'STL100', 'BLK100', 'TOV100', 'PF100', 'PM100']}
    
    return {
        'PTS100': (stats_dict.get('PTS', 0) or 0) * 100 / player_poss,
        'AST100': (stats_dict.get('AST', 0) or 0) * 100 / player_poss,
        'ORB100': (stats_dict.get('OREB', 0) or 0) * 100 / player_poss,
        'DRB100': (stats_dict.get('DREB', 0) or 0) * 100 / player_poss,
        'STL100': (stats_dict.get('STL', 0) or 0) * 100 / player_poss,
        'BLK100': (stats_dict.get('BLK', 0) or 0) * 100 / player_poss,
        'TOV100': (stats_dict.get('TOV', 0) or 0) * 100 / player_poss,
        'PF100': (stats_dict.get('PF', 0) or 0) * 100 / player_poss,
        'PM100': (stats_dict.get('PLUS_MINUS', 0) or 0) * 100 / player_poss
    }

def calculate_true_shooting(stats_dict):
    """
    Calculate True Shooting Percentage
    
    TS% = PTS / (2 × TSA)
    TSA = FGA + 0.44 × FTA
    
    Args:
        stats_dict (dict): Player statistics dictionary
    
    Returns:
        float: True Shooting Percentage
    """
    pts = stats_dict.get('PTS', 0) or 0
    fga = stats_dict.get('FGA', 0) or 0
    fta = stats_dict.get('FTA', 0) or 0
    
    tsa = fga + 0.44 * fta
    
    if tsa <= 0:
        return 0.0
    
    return pts / (2 * tsa)

def assign_position_group(stats_dict):
    """
    Assign position group based on player stats
    GUARD, WING, BIG
    
    Args:
        stats_dict (dict): Player statistics
    
    Returns:
        str: Position group
    """
    # Simple heuristic based on rebounds and assists
    reb_per_game = (stats_dict.get('OREB', 0) + stats_dict.get('DREB', 0)) / max(stats_dict.get('GP', 1), 1)
    ast_per_game = stats_dict.get('AST', 0) / max(stats_dict.get('GP', 1), 1)
    
    if reb_per_game >= 7.0:  # High rebounding = BIG
        return 'BIG'
    elif ast_per_game >= 4.0:  # High assists = GUARD
        return 'GUARD'
    else:  # Default = WING
        return 'WING'

def calculate_defensive_per_100_stats(stats_dict):
    """
    Calculate defensive per-100 possession stats
    
    Args:
        stats_dict (dict): Player statistics dictionary
    
    Returns:
        dict: Defensive per-100 possession statistics
    """
    minutes = stats_dict.get('MIN', 0) or 0
    player_poss = calculate_player_possessions(minutes)
    
    if player_poss <= 0:
        return {'DRB100': 0.0, 'STL100': 0.0, 'BLK100': 0.0, 'PF100': 0.0}
    
    return {
        'DRB100': (stats_dict.get('DREB', 0) or 0) * 100 / player_poss,
        'STL100': (stats_dict.get('STL', 0) or 0) * 100 / player_poss,
        'BLK100': (stats_dict.get('BLK', 0) or 0) * 100 / player_poss,
        'PF100': (stats_dict.get('PF', 0) or 0) * 100 / player_poss
    }

def calculate_position_based_z_scores(all_players_data, min_minutes=200):
    """
    Calculate z-scores for defensive stats by position group
    
    Args:
        all_players_data (list): List of player stat dictionaries
        min_minutes (int): Minimum minutes for calculations
    
    Returns:
        dict: Position-based league means and standard deviations
    """
    import numpy as np
    
    # Filter qualified players and assign positions
    qualified_players = []
    for p in all_players_data:
        if (p.get('MIN', 0) or 0) >= min_minutes:
            p['POSITION_GROUP'] = assign_position_group(p)
            qualified_players.append(p)
    
    if len(qualified_players) == 0:
        qualified_players = [dict(p, POSITION_GROUP=assign_position_group(p)) for p in all_players_data]
    
    # Calculate defensive stats for all qualified players
    all_def_100 = [calculate_defensive_per_100_stats(p) for p in qualified_players]
    all_per_100 = [calculate_per_100_stats(p) for p in qualified_players]
    all_ts = [calculate_true_shooting(p) for p in qualified_players]
    
    # Organize by position group
    position_groups = {'GUARD': [], 'WING': [], 'BIG': []}
    
    for i, p in enumerate(qualified_players):
        pos = p['POSITION_GROUP']
        position_groups[pos].append({
            'def_stats': all_def_100[i],
            'per_100': all_per_100[i],
            'ts': all_ts[i]
        })
    
    # Calculate position-specific defensive stats
    position_stats = {}
    
    for pos, players in position_groups.items():
        if len(players) < 3:  # Fallback to combined stats if too few players
            continue
            
        def_arrays = {
            'DRB100': np.array([p['def_stats']['DRB100'] for p in players]),
            'STL100': np.array([p['def_stats']['STL100'] for p in players]),
            'BLK100': np.array([p['def_stats']['BLK100'] for p in players]),
            'PF100': np.array([p['def_stats']['PF100'] for p in players])
        }
        
        position_stats[pos] = {}
        for stat, values in def_arrays.items():
            position_stats[pos][f'{stat}_mean'] = np.mean(values)
            position_stats[pos][f'{stat}_std'] = max(np.std(values), 0.1)  # Prevent division by zero
    
    # Calculate league-wide offensive and impact stats (unchanged)
    league_stats = {}
    
    # Offensive stats (league-wide)
    off_arrays = {
        'TS': np.array(all_ts),
        'PTS100': np.array([p['PTS100'] for p in all_per_100]),
        'AST100': np.array([p['AST100'] for p in all_per_100]),
        'ORB100': np.array([p['ORB100'] for p in all_per_100]),
        'TOV100': np.array([p['TOV100'] for p in all_per_100]),
        'PM100': np.array([p['PM100'] for p in all_per_100])
    }
    
    for stat, values in off_arrays.items():
        league_stats[f'{stat}_mean'] = np.mean(values)
        league_stats[f'{stat}_std'] = max(np.std(values), 0.1)
    
    # Add position-specific defensive stats
    league_stats['position_stats'] = position_stats
    
    return league_stats
    """
    Calculate z-scores for all relevant stats across all players
    
    Args:
        all_players_data (list): List of player stat dictionaries
        min_minutes (int): Minimum minutes for league averages
    
    Returns:
        dict: League means and standard deviations
    """
    import numpy as np
    
    # Filter qualified players
    qualified_players = [p for p in all_players_data if (p.get('MIN', 0) or 0) >= min_minutes]
    
    if len(qualified_players) == 0:
        # Fallback to all players if no one meets threshold
        qualified_players = all_players_data
    
    # Calculate per-100 stats for all qualified players
    all_per_100 = [calculate_per_100_stats(p) for p in qualified_players]
    all_ts = [calculate_true_shooting(p) for p in qualified_players]
    
    # Calculate league means and stds
    stats_arrays = {
        'TS': np.array(all_ts),
        'PTS100': np.array([p['PTS100'] for p in all_per_100]),
        'AST100': np.array([p['AST100'] for p in all_per_100]),
        'ORB100': np.array([p['ORB100'] for p in all_per_100]),
        'DRB100': np.array([p['DRB100'] for p in all_per_100]),
        'STL100': np.array([p['STL100'] for p in all_per_100]),
        'BLK100': np.array([p['BLK100'] for p in all_per_100]),
        'TOV100': np.array([p['TOV100'] for p in all_per_100]),
        'PF100': np.array([p['PF100'] for p in all_per_100]),
        'PM100': np.array([p['PM100'] for p in all_per_100])
    }
    
    league_stats = {}
    for stat, values in stats_arrays.items():
        league_stats[f'{stat}_mean'] = np.mean(values)
        league_stats[f'{stat}_std'] = np.std(values)
        if league_stats[f'{stat}_std'] <= 0:
            league_stats[f'{stat}_std'] = 1.0  # Prevent division by zero
    
    return league_stats

def calculate_ovibe_z(stats_dict, league_stats):
    """
    Calculate Offensive VIBE z-score component
    
    OVIBE_z = 1.8×z_TS + 1.2×z_PTS100 + 1.3×z_AST100 + 0.8×z_ORB100 - 1.4×z_TOV100
    
    Args:
        stats_dict (dict): Player statistics
        league_stats (dict): League means and standard deviations
    
    Returns:
        float: Offensive VIBE z-score
    """
    per_100 = calculate_per_100_stats(stats_dict)
    ts_pct = calculate_true_shooting(stats_dict)
    
    # Calculate z-scores
    z_ts = (ts_pct - league_stats['TS_mean']) / league_stats['TS_std']
    z_pts100 = (per_100['PTS100'] - league_stats['PTS100_mean']) / league_stats['PTS100_std']
    z_ast100 = (per_100['AST100'] - league_stats['AST100_mean']) / league_stats['AST100_std']
    z_orb100 = (per_100['ORB100'] - league_stats['ORB100_mean']) / league_stats['ORB100_std']
    z_tov100 = (per_100['TOV100'] - league_stats['TOV100_mean']) / league_stats['TOV100_std']
    
    # Weighted combination
    ovibe_z = 1.8*z_ts + 1.2*z_pts100 + 1.3*z_ast100 + 0.8*z_orb100 - 1.4*z_tov100
    
    return ovibe_z

def calculate_dvibe_z(stats_dict, league_stats):
    """
    Calculate Defensive VIBE z-score component with position-based normalization
    
    NEW DVIBE_z = 1.3×z_STL100 + 1.1×z_BLK100 + 0.5×z_DRB100 - 1.0×z_PF100
    (All defensive stats normalized within position groups)
    
    Args:
        stats_dict (dict): Player statistics
        league_stats (dict): League means and standard deviations
    
    Returns:
        float: Defensive VIBE z-score
    """
    def_100 = calculate_defensive_per_100_stats(stats_dict)
    position = assign_position_group(stats_dict)
    
    # Get position-specific stats or fall back to league-wide
    position_stats = league_stats.get('position_stats', {})
    pos_stats = position_stats.get(position, {})
    
    # If no position-specific stats available, use league averages as fallback
    if not pos_stats:
        # Use basic league-wide defensive averages
        z_stl100 = 0.0
        z_blk100 = 0.0
        z_drb100 = 0.0
        z_pf100 = 0.0
    else:
        # Calculate z-scores using position-specific means/stds
        z_stl100 = (def_100['STL100'] - pos_stats.get('STL100_mean', 0)) / pos_stats.get('STL100_std', 1)
        z_blk100 = (def_100['BLK100'] - pos_stats.get('BLK100_mean', 0)) / pos_stats.get('BLK100_std', 1)
        z_drb100 = (def_100['DRB100'] - pos_stats.get('DRB100_mean', 0)) / pos_stats.get('DRB100_std', 1)
        z_pf100 = (def_100['PF100'] - pos_stats.get('PF100_mean', 0)) / pos_stats.get('PF100_std', 1)
    
    # NEW weighted combination with updated weights
    dvibe_z = 1.3*z_stl100 + 1.1*z_blk100 + 0.5*z_drb100 - 1.0*z_pf100
    
    return dvibe_z

def calculate_impact_z(stats_dict, league_stats):
    """
    Calculate Impact z-score from plus-minus
    
    Impact_z = z_PM100 (plus-minus per 100 possessions)
    
    Args:
        stats_dict (dict): Player statistics
        league_stats (dict): League means and standard deviations
    
    Returns:
        float: Impact z-score
    """
    per_100 = calculate_per_100_stats(stats_dict)
    
    z_pm = (per_100['PM100'] - league_stats['PM100_mean']) / league_stats['PM100_std']
    
    return z_pm

def calculate_defensive_raw(stats_dict):
    """
    Calculate raw defensive value
    D_raw = 1.0*DRB + 1.5*STL + 1.3*BLK - 0.5*PF
    
    Args:
        stats_dict (dict): Dictionary containing player statistics
    
    Returns:
        float: Raw defensive value
    """
    drb = stats_dict.get('DREB', 0) or 0
    stl = stats_dict.get('STL', 0) or 0
    blk = stats_dict.get('BLK', 0) or 0
    pf = stats_dict.get('PF', 0) or 0
    
    d_raw = (1.0 * drb + 
             1.5 * stl + 
             1.3 * blk - 
             0.5 * pf)
    
    return d_raw

def calculate_vibe_box_score(stats_dict):
    """
    Calculate box-score VIBE without APM
    
    Args:
        stats_dict (dict): Dictionary containing player statistics
    
    Returns:
        float: Box-score VIBE value
    """
    minutes = stats_dict.get('MIN', 0) or 0
    if minutes <= 0:
        return 0.0
    
    # Step 1: Calculate player possessions
    player_poss = calculate_player_possessions(minutes)
    
    # Step 2: Calculate offensive VIBE
    o_raw = calculate_offensive_raw(stats_dict)
    ovibe = 100 * o_raw / player_poss if player_poss > 0 else 0
    
    # Step 3: Calculate defensive VIBE  
    d_raw = calculate_defensive_raw(stats_dict)
    dvibe = 100 * d_raw / player_poss if player_poss > 0 else 0
    
    # Step 4: Combine offense and defense (offense weighted more)
    vibe_box = 0.6 * ovibe + 0.4 * dvibe
    
    return vibe_box

def calculate_vibe_advanced(stats_dict, league_stats=None):
    """
    Calculate Official VIBE using complete formula with z-scores
    
    Args:
        stats_dict (dict): Player statistics dictionary
        league_stats (dict): League means and standard deviations
    
    Returns:
        dict: Complete VIBE breakdown with components
    """
    if league_stats is None:
        # If no league stats provided, use simplified calculation
        return calculate_vibe_box_score(stats_dict)
    
    # Step 1: Calculate component z-scores
    ovibe_z = calculate_ovibe_z(stats_dict, league_stats)
    dvibe_z = calculate_dvibe_z(stats_dict, league_stats)
    impact_z = calculate_impact_z(stats_dict, league_stats)
    
    # Step 2: Combine into skill component (60% offense, 40% defense)
    skill_z = 0.6 * ovibe_z + 0.4 * dvibe_z
    
    # Step 3: NEW BLEND - Increased impact weight to 35%
    vibe_raw = 0.65 * skill_z + 0.35 * impact_z
    
    # Step 4: Minutes-based shrinkage for stability
    minutes = stats_dict.get('MIN', 0) or 0
    shrink_factor = minutes / (minutes + 600)
    vibe_shrunk = vibe_raw * shrink_factor
    
    return {
        'OVIBE': ovibe_z,
        'DVIBE': dvibe_z,
        'Impact': impact_z,
        'Skill': skill_z,
        'VIBE_raw': vibe_raw,
        'VIBE_shrunk': vibe_shrunk,
        'minutes': minutes,
        'shrink_factor': shrink_factor
    }

def calculate_final_vibe_scores(all_vibe_results):
    """
    Calculate final VIBE scores with league normalization
    
    Args:
        all_vibe_results (list): List of VIBE result dictionaries
    
    Returns:
        list: Updated results with final VIBE scores
    """
    import numpy as np
    
    # Extract shrunk VIBE scores
    shrunk_scores = [result['VIBE_shrunk'] for result in all_vibe_results]
    
    if len(shrunk_scores) == 0:
        return all_vibe_results
    
    # Calculate league mean and std of shrunk scores
    mean_v = np.mean(shrunk_scores)
    std_v = np.std(shrunk_scores)
    
    if std_v <= 0:
        std_v = 1.0
    
    # Calculate final scores: 100 + 15 × (score - mean) / std
    for result in all_vibe_results:
        vibe_final = 100 + 15 * (result['VIBE_shrunk'] - mean_v) / std_v
        result['VIBE'] = round(vibe_final, 1)
    
    return all_vibe_results



def normalize_vibe_score(vibe_value, league_mean=0, league_std=1):
    """
    Normalize VIBE for clean leaderboard display
    VIBE_Score = 100 + 15 * (VIBE - mean) / std
    
    Args:
        vibe_value (float): Raw VIBE value
        league_mean (float): League average VIBE
        league_std (float): League standard deviation
    
    Returns:
        float: Normalized VIBE score
    """
    if league_std <= 0:
        return 100.0
    
    normalized = 100 + 15 * (vibe_value - league_mean) / league_std
    return round(normalized, 1)

def calculate_vibe_basic(points, assists):
    """
    Calculate basic VIBE score (legacy function for compatibility)
    
    Args:
        points (float): Points per game
        assists (float): Assists per game
    
    Returns:
        float: Basic VIBE score
    """
    if points is None or assists is None:
        return 0.0
    
    return round(points + assists, 2)

def get_vibe_description():
    """
    Return description of what VIBE represents
    
    Returns:
        str: Description of VIBE metric
    """
    return "Valued Impact Basketball Estimate - A comprehensive per-100 possessions metric combining offensive and defensive impact"

def get_vibe_formula():
    """
    Return current VIBE formula
    
    Returns:
        str: Current formula description
    """
    return """VIBE = 0.6 * OVIBE + 0.4 * DVIBE (per 100 possessions)
    With optional RAPM blending: Final VIBE = 0.6 * Box-Score VIBE + 0.4 * RAPM_100
    
OVIBE = 100 * (PTS + 0.7*AST + 0.8*ORB + 0.5*3PM - 0.7*FGMiss - 0.4*FTMiss - TOV) / PlayerPoss
DVIBE = 100 * (DRB + 1.5*STL + 1.3*BLK - 0.5*PF) / PlayerPoss

Where PlayerPoss = (MIN / 48) * TeamPoss (default ~100)
RAPM_100 = Real APM using Ridge regression on stint-level play-by-play data"""
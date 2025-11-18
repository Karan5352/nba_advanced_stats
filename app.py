"""
NBA Data Web App - Neon Orange & Black Theme
Simple Flask app with player and team data pages
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from nba_simple_fetcher import NBADataFetcher, create_dataframes_from_nba_data
from vibe_calculator import calculate_vibe_advanced, calculate_position_based_z_scores, calculate_final_vibe_scores
import os

app = Flask(__name__)

# Global variables to store data
team_stats_df = None
player_stats_df = None
nba_fetcher = None
current_season = '2025-26'
data_cache = {}

def load_nba_data(season='2024-25'):
    """Load NBA data for specified season"""
    global team_stats_df, player_stats_df, nba_fetcher, current_season, data_cache
    
    # Check if data is already cached
    if season in data_cache:
        print(f"Using cached data for {season}")
        team_stats_df = data_cache[season]['teams']
        player_stats_df = data_cache[season]['players']
        current_season = season
        return
    
    print(f"Loading NBA data for {season}...")
    nba_fetcher = NBADataFetcher(season=season, season_type='Regular Season')
    current_season = season
    
    # Fetch essential data
    nba_fetcher.fetch_essential_data()
    
    # Create DataFrames
    all_dataframes = create_dataframes_from_nba_data(nba_fetcher.data)
    
    team_stats_df = all_dataframes.get('league_team_stats')
    player_stats_df = all_dataframes.get('league_player_stats')
    
    # Add advanced metrics
    if team_stats_df is not None:
        add_team_advanced_metrics()
    
    if player_stats_df is not None:
        add_player_advanced_metrics()
    
    # Cache the data
    data_cache[season] = {
        'teams': team_stats_df,
        'players': player_stats_df
    }
    
    print(f"NBA data loaded successfully for {season}!")

def add_team_advanced_metrics():
    """Add advanced metrics to team data"""
    global team_stats_df
    
    # Offensive Rating (Points per 100 possessions estimate)
    team_stats_df['OFF_RATING'] = (team_stats_df['PTS'] / team_stats_df['GP']) * 100
    
    # Defensive Rating (Opponent points per 100 possessions estimate)  
    if 'OPP_PTS' in team_stats_df.columns:
        team_stats_df['DEF_RATING'] = (team_stats_df['OPP_PTS'] / team_stats_df['GP']) * 100
        team_stats_df['NET_RATING'] = team_stats_df['OFF_RATING'] - team_stats_df['DEF_RATING']
    
    # True Shooting Percentage
    if all(col in team_stats_df.columns for col in ['PTS', 'FGA', 'FTA']):
        team_stats_df['TS_PCT'] = team_stats_df['PTS'] / (2 * (team_stats_df['FGA'] + 0.44 * team_stats_df['FTA']))
    
    # Pace (possessions per game estimate)
    if 'FGA' in team_stats_df.columns:
        team_stats_df['PACE'] = team_stats_df['FGA'] + team_stats_df['TOV'] + 0.44 * team_stats_df['FTA']

def add_player_advanced_metrics():
    """Add advanced metrics to player data"""
    global player_stats_df
    
    # Filter players with minimum games
    player_stats_df = player_stats_df[player_stats_df['GP'] >= 10].copy()
    
    # Per-game averages
    player_stats_df['PPG'] = player_stats_df['PTS'] / player_stats_df['GP']
    player_stats_df['RPG'] = player_stats_df['REB'] / player_stats_df['GP']
    player_stats_df['APG'] = player_stats_df['AST'] / player_stats_df['GP']
    
    # True Shooting Percentage
    if all(col in player_stats_df.columns for col in ['PTS', 'FGA', 'FTA']):
        player_stats_df['TS_PCT'] = player_stats_df['PTS'] / (2 * (player_stats_df['FGA'] + 0.44 * player_stats_df['FTA']))
        player_stats_df['TS_PCT'] = player_stats_df['TS_PCT'].fillna(0)
    
    # Player Efficiency Rating (simplified)
    if all(col in player_stats_df.columns for col in ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGA', 'FTA']):
        player_stats_df['PER'] = (player_stats_df['PTS'] + player_stats_df['REB'] + player_stats_df['AST'] + 
                                 player_stats_df['STL'] + player_stats_df['BLK'] - player_stats_df['TOV'] - 
                                 (player_stats_df['FGA'] - player_stats_df['FGM']) - 
                                 (player_stats_df['FTA'] - player_stats_df['FTM'])) / player_stats_df['GP']
    
    # Usage Rate (simplified estimate)
    if 'MIN' in player_stats_df.columns:
        player_stats_df['USG_PCT'] = (player_stats_df['FGA'] + 0.44 * player_stats_df['FTA'] + player_stats_df['TOV']) / player_stats_df['MIN'] * 100
    
    # Calculate league statistics with position-based defensive z-scores
    all_players_data = player_stats_df.to_dict('records')
    league_stats = calculate_position_based_z_scores(all_players_data, min_minutes=200)
    
    # Calculate VIBE using official formula
    vibe_results = []
    for _, row in player_stats_df.iterrows():
        stats_dict = {
            'MIN': row.get('MIN', 0),
            'PTS': row.get('PTS', 0),
            'AST': row.get('AST', 0),
            'OREB': row.get('OREB', 0),
            'DREB': row.get('DREB', 0),
            'FGA': row.get('FGA', 0),
            'FGM': row.get('FGM', 0),
            'FTA': row.get('FTA', 0),
            'FTM': row.get('FTM', 0),
            'TOV': row.get('TOV', 0),
            'STL': row.get('STL', 0),
            'BLK': row.get('BLK', 0),
            'PF': row.get('PF', 0),
            'PLUS_MINUS': row.get('PLUS_MINUS', 0)
        }
        
        vibe_result = calculate_vibe_advanced(stats_dict, league_stats)
        vibe_result['PLAYER_ID'] = row.get('PLAYER_ID')
        vibe_results.append(vibe_result)
    
    # Calculate final VIBE scores with league normalization
    vibe_results = calculate_final_vibe_scores(vibe_results)
    
    # Add VIBE components back to DataFrame
    vibe_df = pd.DataFrame(vibe_results)
    player_stats_df = player_stats_df.merge(vibe_df[['PLAYER_ID', 'OVIBE', 'DVIBE', 'Impact', 'VIBE']], 
                                           on='PLAYER_ID', how='left')
    
    # Fill any missing VIBE scores
    player_stats_df['VIBE'] = player_stats_df['VIBE'].fillna(100.0)
    player_stats_df['OVIBE'] = player_stats_df['OVIBE'].fillna(0.0)
    player_stats_df['DVIBE'] = player_stats_df['DVIBE'].fillna(0.0)
    player_stats_df['Impact'] = player_stats_df['Impact'].fillna(0.0)

@app.route('/')
def players_default():
    """Default to player stats page"""
    season = request.args.get('season', '2025-26')
    if season != current_season:
        load_nba_data(season)
    
    if player_stats_df is None:
        return "Data not loaded yet. Please wait..."
    
    # Debug: Check available columns
    print(f"Season: {season}")
    print(f"Available columns: {list(player_stats_df.columns)}")
    print(f"Player data shape: {player_stats_df.shape}")
    if len(player_stats_df) > 0:
        print(f"Sample data: {player_stats_df.iloc[0].to_dict()}")
    
    # Filter players with enough minutes to qualify (more lenient filtering)
    min_col = 'MIN' if 'MIN' in player_stats_df.columns else 'MINS'
    gp_col = 'GP' if 'GP' in player_stats_df.columns else 'G'
    
    print(f"Using columns for filtering - Minutes: {min_col}, Games: {gp_col}")
    
    # Use more lenient filtering or show all if filtering fails
    try:
        if min_col in player_stats_df.columns and gp_col in player_stats_df.columns:
            # Very lenient filtering - just need some playing time
            qualified_players = player_stats_df[
                (player_stats_df[min_col] >= 5.0) & 
                (player_stats_df[gp_col] >= 5)
            ].copy()
            # If still too few players, just take all with any games played
            if len(qualified_players) < 50:
                qualified_players = player_stats_df[player_stats_df[gp_col] >= 1].copy()
        else:
            # If filtering columns don't exist, show top 200 by points or all players
            if 'PTS' in player_stats_df.columns:
                qualified_players = player_stats_df.nlargest(200, 'PTS').copy()
            else:
                qualified_players = player_stats_df.copy()
    except Exception as e:
        print(f"Filtering error: {e}")
        # Just show all players if filtering fails
        qualified_players = player_stats_df.copy()
    
    print(f"Qualified players after filtering: {len(qualified_players)}")
    
    # Sort by points per game for better display
    if 'PPG' in qualified_players.columns:
        qualified_players = qualified_players.sort_values('PPG', ascending=False)
    elif 'PTS' in qualified_players.columns:
        qualified_players = qualified_players.sort_values('PTS', ascending=False)
    
    # Select relevant columns - now including VIBE components
    display_columns = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'VIBE', 'OVIBE', 'DVIBE', 'Impact', 
                      'PPG', 'RPG', 'APG', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT', 'PER']
    
    # Ensure columns exist
    available_columns = [col for col in display_columns if col in qualified_players.columns]
    player_data = qualified_players[available_columns].round(2)
    
    available_seasons = ['2025-26', '2024-25', '2023-24', '2022-23', '2021-22', '2020-21']
    return render_template('players.html', 
                         players=player_data.to_dict('records'),
                         columns=available_columns,
                         current_season=current_season,
                         available_seasons=available_seasons)

@app.route('/about')
def about():
    """About page with VIBE formula explanation"""
    return render_template('about.html')

@app.route('/teams')
def teams():
    """Team data page"""
    season = request.args.get('season', '2025-26')
    if season != current_season:
        load_nba_data(season)
    
    if team_stats_df is None:
        return "Data not loaded yet. Please wait..."
    
    # Select relevant columns
    display_columns = ['TEAM_NAME', 'W', 'L', 'W_PCT', 'PTS', 'REB', 'AST', 
                      'FG_PCT', 'FG3_PCT', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'TS_PCT']
    
    # Ensure columns exist
    available_columns = [col for col in display_columns if col in team_stats_df.columns]
    team_data = team_stats_df[available_columns].round(2)
    
    # Sort by wins
    if 'W' in team_data.columns:
        team_data = team_data.sort_values('W', ascending=False)
    
    available_seasons = ['2025-26', '2024-25', '2023-24', '2022-23', '2021-22', '2020-21']
    return render_template('teams.html', 
                         teams=team_data.to_dict('records'),
                         columns=available_columns,
                         current_season=current_season,
                         available_seasons=available_seasons)

@app.route('/api/players')
def api_players():
    """API endpoint for player data"""
    if player_stats_df is None:
        return jsonify({'error': 'Data not loaded'})
    return jsonify(player_stats_df.to_dict('records'))

@app.route('/api/teams')
def api_teams():
    """API endpoint for team data"""
    if team_stats_df is None:
        return jsonify({'error': 'Data not loaded'})
    return jsonify(team_stats_df.to_dict('records'))

if __name__ == '__main__':
    # Load data on startup with current season
    load_nba_data('2024-25')
    
    # Production-safe debug setting
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Run the app on port 8000 to avoid conflicts
    app.run(debug=debug_mode, host='0.0.0.0', port=8000)
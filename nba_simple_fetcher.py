"""
NBA Data Fetcher - Simplified Working Version
Fetch essential NBA API data for advanced statistics analysis
"""

import pandas as pd
import numpy as np
from nba_api.stats.endpoints import (
    # Core endpoints that definitely exist
    leaguedashteamstats,
    leaguedashplayerstats,
    leagueleaders,
    leaguestandings,
    teamdashboardbygeneralsplits,
    playerdashboardbygeneralsplits,
    boxscoretraditionalv2,
    boxscoreadvancedv2,
    playercareerstats,
    shotchartdetail
)

from nba_api.stats.static import teams, players
import time
import os
import json
from datetime import datetime

class NBADataFetcher:
    """
    Simplified NBA data fetcher for advanced analytics
    """
    
    def __init__(self, season='2023-24', season_type='Regular Season'):
        """
        Initialize the NBA Data Fetcher
        
        Args:
            season (str): NBA season (e.g., '2023-24')
            season_type (str): 'Regular Season', 'Playoffs', or 'All Star'
        """
        self.season = season
        self.season_type = season_type
        self.data = {}
        
        # Create data directory
        self.data_dir = 'nba_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        print(f"Initialized NBA Data Fetcher for {season} {season_type}")
    
    def _rate_limit(self, delay=0.6):
        """Rate limiting to respect NBA API limits"""
        time.sleep(delay)
    
    def _save_data(self, data, filename):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filename} to {filepath}")
    
    def fetch_league_data(self):
        """Fetch league-wide statistics"""
        print("Fetching league data...")
        
        league_data = {}
        
        try:
            # League team stats
            print("  Fetching league team stats...")
            self._rate_limit()
            league_team_stats = leaguedashteamstats.LeagueDashTeamStats(
                season=self.season, 
                season_type_all_star=self.season_type
            ).get_dict()
            
            # League player stats
            print("  Fetching league player stats...")
            self._rate_limit()
            league_player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=self.season, 
                season_type_all_star=self.season_type
            ).get_dict()
            
            # League leaders (points)
            print("  Fetching league leaders...")
            self._rate_limit()
            league_leaders_pts = leagueleaders.LeagueLeaders(
                season=self.season, 
                season_type_all_star=self.season_type,
                stat_category_abbreviation='PTS'
            ).get_dict()
            
            # League standings
            print("  Fetching league standings...")
            self._rate_limit()
            standings = leaguestandings.LeagueStandings(
                season=self.season
            ).get_dict()
            
            league_data = {
                'team_stats': league_team_stats,
                'player_stats': league_player_stats,
                'leaders': league_leaders_pts,
                'standings': standings
            }
            
        except Exception as e:
            print(f"Error fetching league data: {e}")
        
        self.data['league_data'] = league_data
        self._save_data(league_data, 'league_data')
        print("League data fetch complete!")
        return league_data
    
    def fetch_teams_basic_data(self):
        """Fetch basic team information and stats"""
        print("Fetching teams basic data...")
        
        # Get all teams
        all_teams = teams.get_teams()
        self.data['teams'] = all_teams
        
        # Save team info
        self._save_data(all_teams, 'teams_info')
        print(f"Fetched {len(all_teams)} teams")
        return all_teams
    
    def fetch_players_basic_data(self):
        """Fetch basic player information"""
        print("Fetching players basic data...")
        
        # Get all active players
        all_players = players.get_active_players()
        self.data['players'] = all_players
        
        # Save player info
        self._save_data(all_players, 'players_info')
        print(f"Fetched {len(all_players)} active players")
        return all_players
    
    def fetch_team_detailed_stats(self, team_id, team_name=None):
        """
        Fetch detailed stats for a specific team
        
        Args:
            team_id (int): Team ID
            team_name (str): Team name for logging
        """
        if team_name is None:
            team_name = f"Team {team_id}"
        
        print(f"Fetching detailed stats for {team_name}...")
        
        try:
            self._rate_limit()
            team_stats = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
                team_id=team_id, 
                season=self.season, 
                season_type_all_star=self.season_type
            ).get_dict()
            
            return team_stats
            
        except Exception as e:
            print(f"Error fetching detailed stats for {team_name}: {e}")
            return None
    
    def fetch_player_detailed_stats(self, player_id, player_name=None):
        """
        Fetch detailed stats for a specific player
        
        Args:
            player_id (int): Player ID
            player_name (str): Player name for logging
        """
        if player_name is None:
            player_name = f"Player {player_id}"
        
        print(f"Fetching detailed stats for {player_name}...")
        
        try:
            # Player dashboard stats
            self._rate_limit()
            player_stats = playerdashboardbygeneralsplits.PlayerDashboardByGeneralSplits(
                player_id=player_id, 
                season=self.season, 
                season_type_all_star=self.season_type
            ).get_dict()
            
            # Player career stats
            self._rate_limit()
            career_stats = playercareerstats.PlayerCareerStats(
                player_id=player_id
            ).get_dict()
            
            return {
                'dashboard_stats': player_stats,
                'career_stats': career_stats
            }
            
        except Exception as e:
            print(f"Error fetching detailed stats for {player_name}: {e}")
            return None
    
    def fetch_game_data(self, game_id):
        """
        Fetch detailed game data
        
        Args:
            game_id (str): NBA game ID
        """
        print(f"Fetching game data for game {game_id}...")
        
        try:
            # Traditional box score
            self._rate_limit()
            traditional_boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(
                game_id=game_id
            ).get_dict()
            
            # Advanced box score
            self._rate_limit()
            advanced_boxscore = boxscoreadvancedv2.BoxScoreAdvancedV2(
                game_id=game_id
            ).get_dict()
            
            game_data = {
                'game_id': game_id,
                'traditional_boxscore': traditional_boxscore,
                'advanced_boxscore': advanced_boxscore
            }
            
            return game_data
            
        except Exception as e:
            print(f"Error fetching game data: {e}")
            return None
    
    def fetch_shot_chart_data(self, player_id, team_id=0):
        """
        Fetch shot chart data for a player
        
        Args:
            player_id (int): Player ID
            team_id (int): Team ID (0 for all teams)
        """
        print(f"Fetching shot chart data for player {player_id}...")
        
        try:
            self._rate_limit()
            shot_chart = shotchartdetail.ShotChartDetail(
                team_id=team_id,
                player_id=player_id,
                season_nullable=self.season,
                season_type_all_star=self.season_type
            ).get_dict()
            
            return shot_chart
            
        except Exception as e:
            print(f"Error fetching shot chart data: {e}")
            return None
    
    def fetch_essential_data(self):
        """Fetch essential NBA data for analysis"""
        print("Starting essential NBA data fetch...")
        
        # Fetch core data
        self.fetch_league_data()
        self.fetch_teams_basic_data()
        self.fetch_players_basic_data()
        
        # Save complete dataset
        self._save_data(self.data, 'essential_nba_data')
        
        print(f"\nEssential data fetch complete! Data saved in '{self.data_dir}' directory")
        print("\nFetched data includes:")
        print("- League team and player statistics")
        print("- League leaders and standings")
        print("- All teams and players information")
        
        return self.data
    
    def get_data_summary(self):
        """Get summary of fetched data"""
        summary = {
            'total_teams': len(self.data.get('teams', [])),
            'total_players': len(self.data.get('players', [])),
            'league_data_available': bool(self.data.get('league_data')),
            'season': self.season,
            'season_type': self.season_type,
            'data_directory': self.data_dir
        }
        return summary

def create_dataframes_from_nba_data(nba_data):
    """
    Convert NBA API data to pandas DataFrames for easier analysis
    """
    dataframes = {}
    
    # Convert league team stats
    if 'league_data' in nba_data and 'team_stats' in nba_data['league_data']:
        try:
            team_stats_data = nba_data['league_data']['team_stats']['resultSets'][0]
            dataframes['league_team_stats'] = pd.DataFrame(
                team_stats_data['rowSet'], 
                columns=team_stats_data['headers']
            )
            print("Created league_team_stats DataFrame")
        except Exception as e:
            print(f"Could not create league team stats DataFrame: {e}")
    
    # Convert league player stats
    if 'league_data' in nba_data and 'player_stats' in nba_data['league_data']:
        try:
            player_stats_data = nba_data['league_data']['player_stats']['resultSets'][0]
            dataframes['league_player_stats'] = pd.DataFrame(
                player_stats_data['rowSet'], 
                columns=player_stats_data['headers']
            )
            print("Created league_player_stats DataFrame")
        except Exception as e:
            print(f"Could not create league player stats DataFrame: {e}")
    
    # Convert league leaders
    if 'league_data' in nba_data and 'leaders' in nba_data['league_data']:
        try:
            leaders_data = nba_data['league_data']['leaders']['resultSets'][0]
            dataframes['league_leaders'] = pd.DataFrame(
                leaders_data['rowSet'], 
                columns=leaders_data['headers']
            )
            print("Created league_leaders DataFrame")
        except Exception as e:
            print(f"Could not create league leaders DataFrame: {e}")
    
    # Convert standings
    if 'league_data' in nba_data and 'standings' in nba_data['league_data']:
        try:
            standings_data = nba_data['league_data']['standings']['resultSets'][0]
            dataframes['standings'] = pd.DataFrame(
                standings_data['rowSet'], 
                columns=standings_data['headers']
            )
            print("Created standings DataFrame")
        except Exception as e:
            print(f"Could not create standings DataFrame: {e}")
    
    # Convert teams info
    if 'teams' in nba_data:
        try:
            dataframes['teams_info'] = pd.DataFrame(nba_data['teams'])
            print("Created teams_info DataFrame")
        except Exception as e:
            print(f"Could not create teams info DataFrame: {e}")
    
    # Convert players info
    if 'players' in nba_data:
        try:
            dataframes['players_info'] = pd.DataFrame(nba_data['players'])
            print("Created players_info DataFrame")
        except Exception as e:
            print(f"Could not create players info DataFrame: {e}")
    
    return dataframes

def main():
    """Main function to demonstrate usage"""
    # Initialize fetcher
    fetcher = NBADataFetcher(season='2023-24', season_type='Regular Season')
    
    # Fetch essential data
    all_data = fetcher.fetch_essential_data()
    
    # Create DataFrames
    dfs = create_dataframes_from_nba_data(all_data)
    
    # Print summary
    summary = fetcher.get_data_summary()
    print("\n" + "="*50)
    print("NBA DATA FETCH SUMMARY")
    print("="*50)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\nDataFrames created:")
    for name, df in dfs.items():
        print(f"- {name}: {df.shape}")
    
    return fetcher, all_data, dfs

if __name__ == "__main__":
    fetcher, data, dataframes = main()
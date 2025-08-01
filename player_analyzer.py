import pandas as pd
import numpy as np

class PlayerAnalyzer:
    """Analyzes individual player performance and calculates position-specific scores"""

    def __init__(self):
        # Position-specific weights for performance metrics
        self.position_weights = {
            'Forward': {
                'goals': 0.40,
                'assists': 0.25,
                'appearances': 0.15,
                'market_value': 0.20
            },
            'Midfielder': {
                'goals': 0.20,
                'assists': 0.35,
                'appearances': 0.20,
                'market_value': 0.25
            },
            'Defender': {
                'goals': 0.10,
                'assists': 0.15,
                'clean_sheets': 0.35,
                'appearances': 0.20,
                'market_value': 0.20
            },
            'Goalkeeper': {
                'saves': 0.40,
                'clean_sheets': 0.35,
                'appearances': 0.15,
                'market_value': 0.10
            }
        }

    def calculate_player_scores(self, players_data, position):
        """Calculate performance scores for players in a specific position"""
        if players_data.empty:
            return {}

        position_players = players_data[players_data['position'] == position].copy()
        if position_players.empty:
            return {}

        scores = {}
        weights = self.position_weights.get(position, self.position_weights['Forward'])

        # Normalize metrics for this position group
        normalized_data = self._normalize_position_metrics(position_players, position)

        # Calculate weighted scores
        for _, player in normalized_data.iterrows():
            score = 0
            total_weight = 0

            for metric, weight in weights.items():
                norm_metric = f'{metric}_norm'
                if norm_metric in player and not pd.isna(player[norm_metric]):
                    score += player[norm_metric] * weight
                    total_weight += weight

            # Normalize score to total weight used
            if total_weight > 0:
                score = score / total_weight * 100

            scores[player['name']] = score

        return scores

    def _normalize_position_metrics(self, position_players, position):
        """Normalize metrics specific to each position"""
        normalized_data = position_players.copy()

        # Get metrics to normalize based on position
        metrics_to_normalize = list(self.position_weights[position].keys())

        for metric in metrics_to_normalize:
            if metric in normalized_data.columns:
                max_val = normalized_data[metric].max()
                min_val = normalized_data[metric].min()

                if max_val != min_val and max_val > 0:
                    normalized_data[f'{metric}_norm'] = ((normalized_data[metric] - min_val) / (max_val - min_val)) * 100
                else:
                    normalized_data[f'{metric}_norm'] = 50  # Default middle value

        return normalized_data

    def get_top_players_by_position(self, players_data, position, top_n=10):
        """Get top N players in a specific position across all teams"""
        position_players = players_data[players_data['position'] == position]
        if position_players.empty:
            return pd.DataFrame()

        player_scores = self.calculate_player_scores(position_players, position)

        # Add scores to dataframe
        position_players = position_players.copy()
        position_players['performance_score'] = position_players['name'].map(player_scores)

        # Sort by performance score
        top_players = position_players.nlargest(top_n, 'performance_score')

        return top_players

    def analyze_team_squad(self, players_data, team_name):
        """Provide comprehensive analysis of a team's squad"""
        team_players = players_data[players_data['team'] == team_name]
        if team_players.empty:
            return {}

        analysis = {
            'squad_size': len(team_players),
            'average_age': team_players['age'].mean(),
            'total_market_value': team_players['market_value'].sum(),
            'average_market_value': team_players['market_value'].mean(),
            'total_goals': team_players['goals'].sum(),
            'total_assists': team_players['assists'].sum(),
            'position_breakdown': {},
            'top_performers': {},
            'squad_strengths': [],
            'squad_weaknesses': []
        }

        # Position breakdown
        positions = team_players['position'].unique()
        for position in positions:
            pos_players = team_players[team_players['position'] == position]
            analysis['position_breakdown'][position] = {
                'count': len(pos_players),
                'avg_age': pos_players['age'].mean(),
                'total_market_value': pos_players['market_value'].sum(),
                'total_goals': pos_players['goals'].sum(),
                'total_assists': pos_players['assists'].sum()
            }

            # Get top performer in each position
            player_scores = self.calculate_player_scores(pos_players, position)
            if player_scores:
                top_player = max(player_scores.items(), key=lambda x: x[1])
                analysis['top_performers'][position] = {
                    'name': top_player[0],
                    'score': top_player[1]
                }

        # Squad analysis
        analysis['squad_strengths'], analysis['squad_weaknesses'] = self._analyze_squad_strengths_weaknesses(team_players)

        return analysis

    def _analyze_squad_strengths_weaknesses(self, team_players):
        """Analyze team's squad strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Age analysis
        avg_age = team_players['age'].mean()
        if avg_age < 25:
            strengths.append("Young squad with potential for growth")
        elif avg_age > 30:
            weaknesses.append("Aging squad may need rejuvenation")
        else:
            strengths.append("Good age balance in squad")

        # Market value analysis
        total_value = team_players['market_value'].sum()
        avg_value = team_players['market_value'].mean()

        if avg_value > 30000000:
            strengths.append("High-value players indicating quality")
        elif avg_value < 10000000:
            weaknesses.append("Limited market value may indicate quality concerns")

        # Goals distribution
        forwards = team_players[team_players['position'] == 'Forward']
        if not forwards.empty:
            forward_goals = forwards['goals'].sum()
            total_goals = team_players['goals'].sum()

            if total_goals > 0:
                forward_goal_percentage = forward_goals / total_goals
                if forward_goal_percentage > 0.7:
                    weaknesses.append("Over-reliance on forwards for goals")
                elif forward_goal_percentage < 0.5:
                    strengths.append("Goals spread across different positions")

        # Squad depth analysis
        position_counts = team_players['position'].value_counts()

        if position_counts.get('Goalkeeper', 0) < 2:
            weaknesses.append("Limited goalkeeper options")
        if position_counts.get('Defender', 0) < 6:
            weaknesses.append("Thin defensive options")
        if position_counts.get('Midfielder', 0) < 6:
            weaknesses.append("Limited midfield depth")
        if position_counts.get('Forward', 0) < 4:
            weaknesses.append("Few attacking options")

        return strengths, weaknesses

    def compare_players(self, player1_data, player2_data):
        """Compare two players' performance"""
        if player1_data['position'] != player2_data['position']:
            return {"error": "Players must be in the same position for comparison"}

        position = player1_data['position']

        # Create temporary dataframe for comparison
        temp_df = pd.DataFrame([player1_data, player2_data])
        player_scores = self.calculate_player_scores(temp_df, position)

        comparison = {
            'player1': {
                'name': player1_data['name'],
                'score': player_scores.get(player1_data['name'], 0),
                'stats': self._extract_key_stats(player1_data, position)
            },
            'player2': {
                'name': player2_data['name'],
                'score': player_scores.get(player2_data['name'], 0),
                'stats': self._extract_key_stats(player2_data, position)
            },
            'winner': None,
            'key_differences': []
        }

        # Determine winner
        if comparison['player1']['score'] > comparison['player2']['score']:
            comparison['winner'] = player1_data['name']
        elif comparison['player2']['score'] > comparison['player1']['score']:
            comparison['winner'] = player2_data['name']
        else:
            comparison['winner'] = "Draw"

        # Identify key differences
        comparison['key_differences'] = self._identify_key_differences(player1_data, player2_data, position)

        return comparison

    def _extract_key_stats(self, player_data, position):
        """Extract key statistics based on position"""
        base_stats = {
            'age': player_data['age'],
            'market_value': player_data['market_value'],
            'appearances': player_data['appearances']
        }

        if position == 'Forward':
            base_stats.update({
                'goals': player_data['goals'],
                'assists': player_data['assists']
            })
        elif position == 'Midfielder':
            base_stats.update({
                'goals': player_data['goals'],
                'assists': player_data['assists']
            })
        elif position == 'Defender':
            base_stats.update({
                'goals': player_data['goals'],
                'assists': player_data['assists'],
                'clean_sheets': player_data.get('clean_sheets', 0)
            })
        elif position == 'Goalkeeper':
            base_stats.update({
                'saves': player_data.get('saves', 0),
                'clean_sheets': player_data.get('clean_sheets', 0)
            })

        return base_stats

    def _identify_key_differences(self, player1, player2, position):
        """Identify key performance differences between players"""
        differences = []

        # Age difference
        age_diff = abs(player1['age'] - player2['age'])
        if age_diff >= 5:
            younger = player1['name'] if player1['age'] < player2['age'] else player2['name']
            differences.append(f"{younger} is significantly younger ({age_diff} years difference)")

        # Market value difference
        value_diff = abs(player1['market_value'] - player2['market_value'])
        if value_diff >= 20000000:
            higher_value = player1['name'] if player1['market_value'] > player2['market_value'] else player2['name']
            differences.append(f"{higher_value} has significantly higher market value (€{value_diff:,.0f} difference)")

        # Position-specific differences
        if position in ['Forward', 'Midfielder']:
            goal_diff = abs(player1['goals'] - player2['goals'])
            if goal_diff >= 5:
                higher_goals = player1['name'] if player1['goals'] > player2['goals'] else player2['name']
                differences.append(f"{higher_goals} scored {goal_diff} more goals")

            assist_diff = abs(player1['assists'] - player2['assists'])
            if assist_diff >= 3:
                higher_assists = player1['name'] if player1['assists'] > player2['assists'] else player2['name']
                differences.append(f"{higher_assists} provided {assist_diff} more assists")

        return differences

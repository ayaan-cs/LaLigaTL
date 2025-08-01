import numpy as np

class TierCalculator:
    """Calculates tier rankings for LaLiga teams based on multiple performance metrics"""

    def __init__(self):
        # Weights for different performance aspects
        self.weights = {
            'league_position': 0.35,  # Most important factor
            'goals_scored': 0.15,
            'goals_conceded': 0.15,
            'possession': 0.10,
            'pass_accuracy': 0.10,
            'shots_per_game': 0.08,
            'clean_sheets': 0.07
        }

    def calculate_team_scores(self, teams_data, standings):
        """Calculate comprehensive performance scores for all teams"""
        scores = {}

        # Normalize all metrics to 0-100 scale
        normalized_data = teams_data.copy()

        # Higher is better metrics
        for metric in ['goals_for', 'possession_avg', 'pass_accuracy', 'shots_per_game', 'clean_sheets']:
            max_val = teams_data[metric].max()
            min_val = teams_data[metric].min()
            if max_val != min_val:
                normalized_data[f'{metric}_norm'] = ((teams_data[metric] - min_val) / (max_val - min_val)) * 100
            else:
                normalized_data[f'{metric}_norm'] = 50

        # Lower is better metrics (invert)
        for metric in ['position', 'goals_against']:
            max_val = teams_data[metric].max()
            min_val = teams_data[metric].min()
            if max_val != min_val:
                normalized_data[f'{metric}_norm'] = ((max_val - teams_data[metric]) / (max_val - min_val)) * 100
            else:
                normalized_data[f'{metric}_norm'] = 50

        # Calculate weighted scores
        for _, team in normalized_data.iterrows():
            score = (
                    team['position_norm'] * self.weights['league_position'] +
                    team['goals_for_norm'] * self.weights['goals_scored'] +
                    team['goals_against_norm'] * self.weights['goals_conceded'] +
                    team['possession_avg_norm'] * self.weights['possession'] +
                    team['pass_accuracy_norm'] * self.weights['pass_accuracy'] +
                    team['shots_per_game_norm'] * self.weights['shots_per_game'] +
                    team['clean_sheets_norm'] * self.weights['clean_sheets']
            )

            scores[team['team']] = score

        return scores

    def assign_tiers(self, team_scores):
        """Assign S, A, B, C, D tiers based on performance scores"""
        sorted_teams = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)
        tiers = {}

        # Define tier thresholds based on score distribution
        scores_list = [score for _, score in sorted_teams]

        # S Tier: Top 2-3 teams (typically 90+ scores)
        s_threshold = np.percentile(scores_list, 85)

        # A Tier: Next 3-4 teams (typically 75-90 scores)
        a_threshold = np.percentile(scores_list, 65)

        # B Tier: Next 4-5 teams (typically 55-75 scores)
        b_threshold = np.percentile(scores_list, 40)

        # C Tier: Next 4-5 teams (typically 35-55 scores)
        c_threshold = np.percentile(scores_list, 20)

        # D Tier: Bottom 3-4 teams (typically <35 scores)

        for team, score in sorted_teams:
            if score >= s_threshold:
                tiers[team] = 'S'
            elif score >= a_threshold:
                tiers[team] = 'A'
            elif score >= b_threshold:
                tiers[team] = 'B'
            elif score >= c_threshold:
                tiers[team] = 'C'
            else:
                tiers[team] = 'D'

        # Ensure realistic tier distribution
        tiers = self._balance_tiers(tiers, sorted_teams)

        return tiers

    def _balance_tiers(self, tiers, sorted_teams):
        """Ensure balanced tier distribution"""
        # Count teams in each tier
        tier_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for tier in tiers.values():
            tier_counts[tier] += 1

        # Ideal distribution for 20 teams
        ideal_distribution = {'S': 3, 'A': 4, 'B': 5, 'C': 5, 'D': 3}

        # Rebalance if necessary
        balanced_tiers = {}
        tier_order = ['S', 'A', 'B', 'C', 'D']
        current_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}

        for team, score in sorted_teams:
            assigned = False
            for tier in tier_order:
                if current_counts[tier] < ideal_distribution[tier]:
                    balanced_tiers[team] = tier
                    current_counts[tier] += 1
                    assigned = True
                    break

            if not assigned:
                # Fill remaining teams in the last available tier
                for tier in reversed(tier_order):
                    if current_counts[tier] < ideal_distribution[tier]:
                        balanced_tiers[team] = tier
                        current_counts[tier] += 1
                        break

        return balanced_tiers

    def get_tier_analysis(self, teams_data, tiers):
        """Provide detailed analysis for each tier"""
        analysis = {}

        for tier in ['S', 'A', 'B', 'C', 'D']:
            tier_teams = [team for team, t in tiers.items() if t == tier]
            if tier_teams:
                tier_data = teams_data[teams_data['team'].isin(tier_teams)]

                analysis[tier] = {
                    'teams': tier_teams,
                    'count': len(tier_teams),
                    'avg_points': tier_data['points'].mean(),
                    'avg_goals_for': tier_data['goals_for'].mean(),
                    'avg_goals_against': tier_data['goals_against'].mean(),
                    'avg_possession': tier_data['possession_avg'].mean(),
                    'characteristics': self._get_tier_characteristics(tier)
                }

        return analysis

    def _get_tier_characteristics(self, tier):
        """Define characteristics for each tier"""
        characteristics = {
            'S': [
                "Elite teams competing for titles",
                "Exceptional attacking and defensive balance",
                "High possession and pass accuracy",
                "World-class players in key positions",
                "Consistent performance throughout season"
            ],
            'A': [
                "Strong teams competing for European qualification",
                "Good balance between attack and defense",
                "Solid tactical organization",
                "Quality squad depth",
                "Capable of beating top teams on their day"
            ],
            'B': [
                "Mid-table teams with clear strengths",
                "May excel in specific areas (attack/defense)",
                "Inconsistent performance levels",
                "Limited squad depth",
                "Fighting for European spots or avoiding relegation"
            ],
            'C': [
                "Teams struggling for consistency",
                "Defensive or attacking weaknesses",
                "Reliant on key players",
                "Limited financial resources",
                "Fighting to avoid relegation"
            ],
            'D': [
                "Teams with significant weaknesses",
                "Poor defensive organization",
                "Limited attacking threat",
                "Squad quality concerns",
                "High risk of relegation"
            ]
        }

        return characteristics.get(tier, [])

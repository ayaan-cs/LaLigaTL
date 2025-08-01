import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class Visualizations:
    """Creates all visualizations for the LaLiga analysis application"""

    def __init__(self):
        # Color schemes for different tiers
        self.tier_colors = {
            'S': '#FFD700',  # Gold
            'A': '#C0C0C0',  # Silver
            'B': '#CD7F32',  # Bronze
            'C': '#32CD32',  # Green
            'D': '#FF6347'   # Red
        }

        self.team_colors = {
            'Barcelona': '#A50044',
            'Real Madrid': '#FEBE10',
            'Atlético Madrid': '#CE1126',
            'Athletic Bilbao': '#EE2523',
            'Villarreal': '#FFFF00',
            'Real Betis': '#00954C',
            'Sevilla': '#D0103A',
            'Real Sociedad': '#0078B9',
            'Valencia': '#FF8F00',
            'Osasuna': '#DA020E'
        }

    def create_tier_visualization(self, tiers):
        """Create an interactive tier ranking visualization"""
        # Count teams in each tier
        tier_counts = {}
        for tier in ['S', 'A', 'B', 'C', 'D']:
            tier_counts[tier] = len([t for t in tiers.values() if t == tier])

        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(tier_counts.keys()),
                y=list(tier_counts.values()),
                marker_color=[self.tier_colors[tier] for tier in tier_counts.keys()],
                text=list(tier_counts.values()),
                textposition='auto',
                hovertemplate='<b>Tier %{x}</b><br>Teams: %{y}<extra></extra>'
            )
        ])

        fig.update_layout(
            title="LaLiga Teams Distribution by Tier",
            xaxis_title="Tier",
            yaxis_title="Number of Teams",
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Create tier breakdown table
        tier_data = []
        for tier in ['S', 'A', 'B', 'C', 'D']:
            tier_teams = [team for team, t in tiers.items() if t == tier]
            if tier_teams:
                tier_data.append({
                    'Tier': tier,
                    'Teams': ', '.join(tier_teams),
                    'Count': len(tier_teams)
                })

        if tier_data:
            tier_df = pd.DataFrame(tier_data)
            st.dataframe(tier_df, use_container_width=True, hide_index=True)

    def create_player_comparison(self, players_data, position):
        """Create player comparison visualization"""
        if len(players_data) < 2:
            st.info("Need at least 2 players for comparison")
            return

        # Select metrics based on position
        if position == 'Forward':
            metrics = ['goals', 'assists', 'market_value', 'appearances']
            metric_labels = ['Goals', 'Assists', 'Market Value (M€)', 'Appearances']
        elif position == 'Midfielder':
            metrics = ['goals', 'assists', 'market_value', 'appearances']
            metric_labels = ['Goals', 'Assists', 'Market Value (M€)', 'Appearances']
        elif position == 'Defender':
            metrics = ['goals', 'assists', 'clean_sheets', 'market_value']
            metric_labels = ['Goals', 'Assists', 'Clean Sheets', 'Market Value (M€)']
        else:  # Goalkeeper
            metrics = ['saves', 'clean_sheets', 'market_value', 'appearances']
            metric_labels = ['Saves', 'Clean Sheets', 'Market Value (M€)', 'Appearances']

        # Prepare data for radar chart (top 5 players)
        top_players = players_data.head(5)

        fig = go.Figure()

        for idx, player in top_players.iterrows():
            values = []
            for metric in metrics:
                val = player.get(metric, 0)
                if metric == 'market_value':
                    val = val / 1000000  # Convert to millions
                values.append(val)

            # Close the radar chart
            values.append(values[0])
            labels = metric_labels + [metric_labels[0]]

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=player['name'],
                line=dict(width=2),
                opacity=0.7
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([max([player.get(m, 0) if m != 'market_value' else player.get(m, 0)/1000000 for m in metrics]) for _, player in top_players.iterrows()])]
                )),
            title=f"Top {position}s Comparison",
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_goals_position_chart(self, teams_data):
        """Create goals vs league position scatter plot"""
        fig = px.scatter(
            teams_data,
            x='position',
            y='goals_for',
            size='market_value' if 'market_value' in teams_data.columns else 'goals_for',
            color='goal_difference',
            hover_name='team',
            hover_data=['goals_against', 'points'],
            color_continuous_scale='RdYlGn',
            title="Goals Scored vs League Position"
        )

        fig.update_layout(
            xaxis_title="League Position",
            yaxis_title="Goals Scored",
            xaxis=dict(autorange="reversed"),  # Reverse x-axis so position 1 is on the right
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_market_value_distribution(self, players_data):
        """Create market value distribution visualization"""
        # Create bins for market value
        players_data['value_category'] = pd.cut(
            players_data['market_value'],
            bins=[0, 10000000, 25000000, 50000000, 100000000, float('inf')],
            labels=['<€10M', '€10-25M', '€25-50M', '€50-100M', '€100M+']
        )

        # Count by category and position
        value_counts = players_data.groupby(['value_category', 'position']).size().reset_index(name='count')

        fig = px.bar(
            value_counts,
            x='value_category',
            y='count',
            color='position',
            title="Player Market Value Distribution by Position",
            barmode='stack'
        )

        fig.update_layout(
            xaxis_title="Market Value Range",
            yaxis_title="Number of Players",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_team_performance_matrix(self, teams_data):
        """Create team performance matrix comparing attack vs defense"""
        fig = px.scatter(
            teams_data,
            x='goals_against',
            y='goals_for',
            size='points',
            color='position',
            hover_name='team',
            hover_data=['points', 'goal_difference'],
            color_continuous_scale='RdYlGn_r',
            title="Team Performance Matrix: Attack vs Defense"
        )

        # Add quadrant lines
        avg_goals_for = teams_data['goals_for'].mean()
        avg_goals_against = teams_data['goals_against'].mean()

        fig.add_hline(y=avg_goals_for, line_dash="dash", line_color="gray", annotation_text="Avg Goals For")
        fig.add_vline(x=avg_goals_against, line_dash="dash", line_color="gray", annotation_text="Avg Goals Against")

        fig.update_layout(
            xaxis_title="Goals Conceded",
            yaxis_title="Goals Scored",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_correlation_heatmap(self, correlation_data):
        """Create correlation heatmap for team performance metrics"""
        fig = px.imshow(
            correlation_data,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Team Performance Metrics Correlation"
        )

        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

        # Add insights
        st.markdown("### 🔍 Correlation Insights")

        # Find strongest correlations
        correlations = []
        for i in range(len(correlation_data.columns)):
            for j in range(i+1, len(correlation_data.columns)):
                corr_value = correlation_data.iloc[i, j]
                correlations.append({
                    'metric1': correlation_data.columns[i],
                    'metric2': correlation_data.columns[j],
                    'correlation': abs(corr_value),
                    'direction': 'positive' if corr_value > 0 else 'negative'
                })

        # Sort by correlation strength
        correlations.sort(key=lambda x: x['correlation'], reverse=True)

        for corr in correlations[:3]:  # Top 3 correlations
            direction_emoji = "📈" if corr['direction'] == 'positive' else "📉"
            st.markdown(f"{direction_emoji} **{corr['metric1']}** and **{corr['metric2']}** have a {corr['direction']} correlation of {corr['correlation']:.2f}")

    def create_season_timeline(self, teams_data):
        """Create a timeline showing key season events"""
        # This would typically use real match data, but we'll create a summary view

        # Create key events based on final standings
        events = [
            {"date": "2024-08-15", "event": "Season Started", "team": "All Teams"},
            {"date": "2024-12-22", "event": "Winter Break", "team": "All Teams"},
            {"date": "2025-04-25", "event": "Real Valladolid Relegated", "team": "Real Valladolid"},
            {"date": "2025-05-14", "event": "Las Palmas Relegated", "team": "Las Palmas"},
            {"date": "2025-05-15", "event": "Barcelona Crowned Champions", "team": "Barcelona"},
            {"date": "2025-05-25", "event": "Season Ended", "team": "All Teams"}
        ]

        events_df = pd.DataFrame(events)
        events_df['date'] = pd.to_datetime(events_df['date'])

        fig = px.timeline(
            events_df,
            x_start='date',
            x_end='date',
            y='team',
            color='team',
            title="LaLiga 2024-25 Season Key Events"
        )

        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

    def create_position_breakdown_chart(self, players_data):
        """Create position breakdown visualization"""
        position_stats = players_data.groupby('position').agg({
            'goals': 'sum',
            'assists': 'sum',
            'market_value': 'mean',
            'age': 'mean'
        }).reset_index()

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Goals by Position', 'Assists by Position',
                            'Avg Market Value', 'Average Age'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )

        # Goals
        fig.add_trace(
            go.Bar(x=position_stats['position'], y=position_stats['goals'],
                   name="Goals", marker_color='lightblue'),
            row=1, col=1
        )

        # Assists
        fig.add_trace(
            go.Bar(x=position_stats['position'], y=position_stats['assists'],
                   name="Assists", marker_color='lightgreen'),
            row=1, col=2
        )

        # Market Value
        fig.add_trace(
            go.Bar(x=position_stats['position'], y=position_stats['market_value']/1000000,
                   name="Avg Value (M€)", marker_color='gold'),
            row=2, col=1
        )

        # Age
        fig.add_trace(
            go.Bar(x=position_stats['position'], y=position_stats['age'],
                   name="Avg Age", marker_color='coral'),
            row=2, col=2
        )

        fig.update_layout(height=600, showlegend=False, title_text="Position Analysis Overview")

        st.plotly_chart(fig, use_container_width=True)

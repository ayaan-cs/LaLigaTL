import streamlit as st

from data_processor import DataProcessor
from tier_calculator import TierCalculator
from player_analyzer import PlayerAnalyzer
from visualizations import Visualizations

# Page configuration
st.set_page_config(
    page_title="LaLiga Tier Rankings 2024-25",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .tier-s { background: linear-gradient(45deg, #FFD700, #FFA500); color: black; }
    .tier-a { background: linear-gradient(45deg, #C0C0C0, #A0A0A0); color: black; }
    .tier-b { background: linear-gradient(45deg, #CD7F32, #8B4513); color: white; }
    .tier-c { background: linear-gradient(45deg, #32CD32, #228B22); color: white; }
    .tier-d { background: linear-gradient(45deg, #FF6347, #DC143C); color: white; }
    
    .tier-card {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 2px solid #ddd;
        text-align: center;
        font-weight: bold;
    }
    
    .stat-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("⚽ LaLiga Tier Rankings 2024-25")
    st.markdown("**Comprehensive analysis of all 20 LaLiga teams and players based on performance, value, and role-specific metrics**")

    # Initialize data processors
    data_processor = DataProcessor()
    tier_calculator = TierCalculator()
    player_analyzer = PlayerAnalyzer()
    visualizations = Visualizations()

    # Load and process data
    with st.spinner("Loading LaLiga 2024-25 season data..."):
        teams_data = data_processor.get_teams_data()
        players_data = data_processor.get_players_data()
        standings = data_processor.get_final_standings()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis",
        ["🏆 Team Tier Rankings", "👥 Player Analysis", "📊 Statistical Dashboard", "📈 Performance Insights", "💾 Export Data"]
    )

    if page == "🏆 Team Tier Rankings":
        show_team_tier_rankings(teams_data, standings, tier_calculator, visualizations)
    elif page == "👥 Player Analysis":
        show_player_analysis(players_data, teams_data, player_analyzer, visualizations)
    elif page == "📊 Statistical Dashboard":
        show_statistical_dashboard(teams_data, players_data, standings, visualizations)
    elif page == "📈 Performance Insights":
        show_performance_insights(teams_data, players_data, visualizations)
    elif page == "💾 Export Data":
        show_export_options(teams_data, players_data, standings)

def show_team_tier_rankings(teams_data, standings, tier_calculator, visualizations):
    st.header("🏆 LaLiga Team Tier Rankings")

    # Calculate tier rankings
    team_scores = tier_calculator.calculate_team_scores(teams_data, standings)
    tiers = tier_calculator.assign_tiers(team_scores)

    # Display season overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Champions", "Barcelona", "28th Title")
    with col2:
        st.metric("🥈 Runner-up", "Real Madrid", "-4 points")
    with col3:
        st.metric("⚽ Top Scorer", "K. Mbappé", "31 goals")
    with col4:
        st.metric("🅰️ Most Assists", "L. Yamal", "13 assists")

    st.markdown("---")

    # Tier visualization
    st.subheader("📊 Tier Distribution")
    visualizations.create_tier_visualization(tiers)

    # Display teams by tier
    tier_names = ['S', 'A', 'B', 'C', 'D']
    tier_colors = ['tier-s', 'tier-a', 'tier-b', 'tier-c', 'tier-d']

    for tier, color in zip(tier_names, tier_colors):
        tier_teams = [team for team, t in tiers.items() if t == tier]
        if tier_teams:
            st.subheader(f"Tier {tier}")

            cols = st.columns(min(len(tier_teams), 4))
            for i, team in enumerate(tier_teams):
                with cols[i % 4]:
                    team_data = teams_data[teams_data['team'] == team].iloc[0]
                    score = team_scores[team]

                    st.markdown(f"""
                    <div class="tier-card {color}">
                        <h4>{team}</h4>
                        <p>Score: {score:.1f}</p>
                        <p>Position: {team_data['position']}</p>
                        <p>Points: {team_data['points']}</p>
                    </div>
                    """, unsafe_allow_html=True)

def show_player_analysis(players_data, teams_data, player_analyzer, visualizations):
    st.header("👥 Player Analysis by Position and Performance")

    # Team selection
    selected_team = st.selectbox("Select Team for Detailed Analysis",
                                 teams_data['team'].unique())

    if selected_team:
        team_players = players_data[players_data['team'] == selected_team]

        # Position tabs
        positions = team_players['position'].unique()
        tabs = st.tabs([f"{pos} ({len(team_players[team_players['position']==pos])})"
                        for pos in positions])

        for i, position in enumerate(positions):
            with tabs[i]:
                position_players = team_players[team_players['position'] == position]

                # Calculate player scores for this position
                player_scores = player_analyzer.calculate_player_scores(position_players, position)

                # Sort by score
                position_players = position_players.copy()
                position_players['score'] = position_players['name'].map(player_scores)
                position_players = position_players.sort_values('score', ascending=False)

                # Display top players
                for idx, player in position_players.iterrows():
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.markdown(f"**{player['name']}** ({player['age']} years)")
                        st.markdown(f"Market Value: €{player['market_value']:,.0f}")

                    with col2:
                        st.metric("Performance Score", f"{player['score']:.1f}")

                    with col3:
                        # Position-specific metrics
                        if position == 'Forward':
                            st.metric("Goals", player['goals'])
                        elif position == 'Midfielder':
                            st.metric("Assists", player['assists'])
                        elif position == 'Defender':
                            st.metric("Clean Sheets", player.get('clean_sheets', 0))
                        elif position == 'Goalkeeper':
                            st.metric("Saves", player.get('saves', 0))

                # Player comparison chart
                if len(position_players) > 1:
                    st.subheader(f"{position} Comparison")
                    visualizations.create_player_comparison(position_players, position)

def show_statistical_dashboard(teams_data, players_data, standings, visualizations):
    st.header("📊 Statistical Dashboard")

    # Key statistics overview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥅 Team Attack Statistics")
        attack_stats = teams_data.nlargest(10, 'goals_for')[['team', 'goals_for', 'shots_per_game']]
        st.dataframe(attack_stats, use_container_width=True)

        st.subheader("🛡️ Team Defense Statistics")
        defense_stats = teams_data.nsmallest(10, 'goals_against')[['team', 'goals_against', 'clean_sheets']]
        st.dataframe(defense_stats, use_container_width=True)

    with col2:
        st.subheader("⭐ Top Individual Performers")

        # Top scorers
        top_scorers = players_data.nlargest(10, 'goals')[['name', 'team', 'goals', 'position']]
        st.markdown("**🥅 Top Scorers**")
        st.dataframe(top_scorers, use_container_width=True)

        # Top assisters
        top_assists = players_data.nlargest(10, 'assists')[['name', 'team', 'assists', 'position']]
        st.markdown("**🅰️ Top Assisters**")
        st.dataframe(top_assists, use_container_width=True)

    # Interactive charts
    st.subheader("📈 Interactive Analysis")

    chart_type = st.selectbox("Choose Chart Type",
                              ["Goals vs Position", "Market Value Distribution", "Team Performance Matrix"])

    if chart_type == "Goals vs Position":
        visualizations.create_goals_position_chart(teams_data)
    elif chart_type == "Market Value Distribution":
        visualizations.create_market_value_distribution(players_data)
    elif chart_type == "Team Performance Matrix":
        visualizations.create_team_performance_matrix(teams_data)

def show_performance_insights(teams_data, players_data, visualizations):
    st.header("📈 Performance Insights & Trends")

    # Performance correlation analysis
    st.subheader("🔍 Performance Correlation Analysis")

    correlation_metrics = ['goals_for', 'goals_against', 'points', 'possession_avg', 'shots_per_game']
    correlation_data = teams_data[correlation_metrics].corr()

    visualizations.create_correlation_heatmap(correlation_data)

    # League averages and benchmarks
    st.subheader("📊 League Benchmarks")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_goals = teams_data['goals_for'].mean()
        st.metric("Average Goals Per Team", f"{avg_goals:.1f}")

        avg_possession = teams_data['possession_avg'].mean()
        st.metric("Average Possession %", f"{avg_possession:.1f}%")

    with col2:
        avg_market_value = players_data['market_value'].mean()
        st.metric("Average Player Value", f"€{avg_market_value:,.0f}")

        total_goals = players_data['goals'].sum()
        st.metric("Total Goals Scored", f"{total_goals}")

    with col3:
        avg_age = players_data['age'].mean()
        st.metric("Average Player Age", f"{avg_age:.1f} years")

        total_assists = players_data['assists'].sum()
        st.metric("Total Assists", f"{total_assists}")

    # Advanced insights
    st.subheader("🧠 Advanced Insights")

    insights = [
        f"🏆 **Champion Analysis**: Barcelona secured the title with {teams_data[teams_data['team']=='Barcelona']['points'].iloc[0]} points, finishing 4 points ahead of Real Madrid.",
        f"⚽ **Goal Scoring**: The league averaged 2.61 goals per game, with Barcelona leading with 102 goals scored.",
        f"🛡️ **Defensive Strength**: Atlético Madrid's Jan Oblak recorded the most clean sheets (15), showcasing defensive excellence.",
        f"💰 **Market Value**: Higher market values correlate with better league positions, but surprises like Girona's previous season show football's unpredictability.",
        f"📈 **Performance Trends**: Teams with higher possession percentages generally scored more goals and achieved better league positions."
    ]

    for insight in insights:
        st.markdown(f"""
        <div class="stat-card">
            {insight}
        </div>
        """, unsafe_allow_html=True)

def show_export_options(teams_data, players_data, standings):
    st.header("💾 Export Data & Results")

    st.subheader("📊 Available Export Options")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Team Data Exports**")

        if st.button("📥 Download Team Rankings CSV"):
            csv = teams_data.to_csv(index=False)
            st.download_button(
                label="Download Team Data",
                data=csv,
                file_name="laliga_team_rankings_2024_25.csv",
                mime="text/csv"
            )

        if st.button("📥 Download Final Standings CSV"):
            csv = standings.to_csv(index=False)
            st.download_button(
                label="Download Standings",
                data=csv,
                file_name="laliga_final_standings_2024_25.csv",
                mime="text/csv"
            )

    with col2:
        st.markdown("**👥 Player Data Exports**")

        if st.button("📥 Download Player Statistics CSV"):
            csv = players_data.to_csv(index=False)
            st.download_button(
                label="Download Player Data",
                data=csv,
                file_name="laliga_player_stats_2024_25.csv",
                mime="text/csv"
            )

        selected_team_export = st.selectbox("Select team for player export",
                                            teams_data['team'].unique())

        if st.button(f"📥 Download {selected_team_export} Players CSV"):
            team_players = players_data[players_data['team'] == selected_team_export]
            csv = team_players.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_team_export} Players",
                data=csv,
                file_name=f"laliga_{selected_team_export.lower().replace(' ', '_')}_players_2024_25.csv",
                mime="text/csv"
            )

    # Summary statistics for export
    st.subheader("📋 Export Summary")

    summary_stats = {
        "Total Teams": len(teams_data),
        "Total Players": len(players_data),
        "Season": "2024-25",
        "Champions": "Barcelona",
        "Top Scorer": "Kylian Mbappé (31 goals)",
        "Most Assists": "Lamine Yamal (13 assists)"
    }

    for key, value in summary_stats.items():
        st.markdown(f"**{key}**: {value}")

if __name__ == "__main__":
    main()

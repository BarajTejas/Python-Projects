import streamlit as st
from modules.db import init_db
from modules.player import register_player, get_players
from modules.team import create_team, get_teams, add_player_to_team, get_players_in_team
from modules.match import create_match, get_matches
from modules.scoring import add_ball_score, get_scores_by_match
from modules.stats import get_player_stats, get_match_summary
from modules.export import export_scores_to_csv
import os

# Initialize DB
init_db()
st.set_page_config(page_title="🏏 Cricheroes Clone", layout="centered")
st.title("🏏 Cricheroes Clone - Python + Streamlit")


# Sidebar menu
menu = st.sidebar.selectbox("📜 Menu", [
    "Register Player", "Create Team", "Assign Players to Team",
    "Create Match", "Scoring", "Match Summary",
    "Player Stats", "Export CSV", "View Match Data", "Reset"
])

# Register Player
if menu == "Register Player":
    st.subheader("👤 Register New Player")
    name = st.text_input("Player Name", key="new_player_name")
    if st.button("Add Player") and name:
        register_player(name)
        st.success(f"✅ Player '{name}' registered.")
        st.experimental_rerun()

    st.subheader("📋 All Players")
    players = get_players()  # expected list of (id, name)

    # Ensure session state keys
    if "editing_player" not in st.session_state:
        st.session_state["editing_player"] = None
    if "editing_name" not in st.session_state:
        st.session_state["editing_name"] = ""
    if "deleting_player" not in st.session_state:
        st.session_state["deleting_player"] = None

    # Show player rows with buttons
    for p in players:
        player_id, player_name = p[0], p[1]
        col_name, col_edit, col_delete = st.columns([3, 1, 1])
        col_name.write(player_name)

        if col_edit.button("Edit", key=f"edit_{player_id}"):
            st.session_state["editing_player"] = player_id
            st.session_state["editing_name"] = player_name

        if col_delete.button("Delete", key=f"del_{player_id}"):
            st.session_state["deleting_player"] = player_id

    # Edit UI
    if st.session_state["editing_player"]:
        pid = st.session_state["editing_player"]
        st.markdown("**✏️ Edit Player**")
        new_name = st.text_input("New name", value=st.session_state.get("editing_name", ""), key="edit_name_input")
        if st.button("Save Changes", key=f"save_{pid}"):
            from modules.player import update_player  # lazy import to avoid circular issues
            update_player(pid, new_name)
            st.success("✅ Player updated.")
            st.session_state["editing_player"] = None
            st.session_state["editing_name"] = ""
            st.experimental_rerun()
        if st.button("Cancel", key=f"cancel_edit_{pid}"):
            st.session_state["editing_player"] = None
            st.session_state["editing_name"] = ""

    # Delete confirmation UI
    if st.session_state["deleting_player"]:
        pid = st.session_state["deleting_player"]
        st.warning("Are you sure you want to delete this player? This action cannot be undone.")
        if st.button("Confirm Delete", key=f"confirm_del_{pid}"):
            from modules.player import delete_player
            delete_player(pid)
            st.success("🗑️ Player deleted.")
            st.session_state["deleting_player"] = None
            st.experimental_rerun()
        if st.button("Cancel", key=f"cancel_del_{pid}"):
            st.session_state["deleting_player"] = None

# Create Team
elif menu == "Create Team":
    st.subheader("🛡️ Create Team")
    team_name = st.text_input("Team Name", key="new_team_name")
    if st.button("Create Team") and team_name:
        create_team(team_name)
        st.success(f"✅ Team '{team_name}' created.")
        st.experimental_rerun()

    st.subheader("📋 All Teams")
    teams = get_teams()  # expect list of (id, name)

    # session state keys
    if "editing_team" not in st.session_state:
        st.session_state["editing_team"] = None
    if "editing_team_name" not in st.session_state:
        st.session_state["editing_team_name"] = ""
    if "deleting_team" not in st.session_state:
        st.session_state["deleting_team"] = None

    # list teams with Edit / Delete buttons
    for t in teams:
        team_id, team_name = t[0], t[1]
        col_name, col_edit, col_delete = st.columns([3, 1, 1])
        col_name.write(team_name)

        if col_edit.button("Edit", key=f"edit_team_{team_id}"):
            st.session_state["editing_team"] = team_id
            st.session_state["editing_team_name"] = team_name

        if col_delete.button("Delete", key=f"del_team_{team_id}"):
            st.session_state["deleting_team"] = team_id

    # Edit form
    if st.session_state["editing_team"]:
        tid = st.session_state["editing_team"]
        st.markdown("**✏️ Edit Team**")
        new_name = st.text_input("New Team Name", value=st.session_state.get("editing_team_name", ""), key=f"edit_team_name_input_{tid}")
        if st.button("Save Team", key=f"save_team_{tid}"):
            from modules.team import update_team
            update_team(tid, new_name)
            st.success("✅ Team updated.")
            st.session_state["editing_team"] = None
            st.session_state["editing_team_name"] = ""
            st.experimental_rerun()
        if st.button("Cancel", key=f"cancel_edit_team_{tid}"):
            st.session_state["editing_team"] = None
            st.session_state["editing_team_name"] = ""

    # Delete confirmation
    if st.session_state["deleting_team"]:
        tid = st.session_state["deleting_team"]
        st.warning("Are you sure you want to delete this team? Matches referencing this team may also be removed.")
        if st.button("Confirm Delete Team", key=f"confirm_del_team_{tid}"):
            from modules.team import delete_team
            delete_team(tid)
            st.success("🗑️ Team deleted.")
            st.session_state["deleting_team"] = None
            st.experimental_rerun()
        if st.button("Cancel", key=f"cancel_del_team_{tid}"):
            st.session_state["deleting_team"] = None

# Assign Players to Team
elif menu == "Assign Players to Team":
    st.subheader("➕ Assign Players")
    teams = get_teams()
    players = get_players()

    team_map = {t[1]: t[0] for t in teams}
    player_map = {p[1]: p[0] for p in players}

    selected_team = st.selectbox("Select Team", list(team_map.keys()))
    selected_players = st.multiselect("Select Players", list(player_map.keys()))

    if st.button("Assign"):
        for player in selected_players:
            add_player_to_team(team_map[selected_team], player_map[player])
        st.success("✅ Players assigned.")

    if selected_team:
        st.subheader("🡭 Players in Team")
        st.table(get_players_in_team(team_map[selected_team]))

# Create Match
elif menu == "Create Match":
    st.subheader("🎮 Create Match")
    teams = get_teams()
    if len(teams) < 2:
        st.warning("⚠️ Need at least 2 teams to start a match.")
    else:
        team_names = [t[1] for t in teams]
        team_map = {t[1]: t[0] for t in teams}

        team1 = st.selectbox("Team 1", team_names)
        team2 = st.selectbox("Team 2", [t for t in team_names if t != team1])
        toss_winner = st.selectbox("Toss Winner", [team1, team2])
        toss_choice = st.radio("Toss Decision", ["Bat", "Bowl"])
        overs = st.number_input("Overs", min_value=1, max_value=50, step=1)
        date = st.date_input("Match Date")

        if st.button("Start Match"):
            create_match(team_map[team1], team_map[team2], team_map[toss_winner], toss_choice, overs, str(date))
            st.success("✅ Match Created.")

# Scoring
elif menu == "Scoring":
    st.subheader("🏏 Add Score")
    matches = get_matches()
    players = get_players()

    if matches and players:
        match_map = {f"Match #{m[0]} - {m[5]}": m[0] for m in matches}
        selected_match = st.selectbox("Select Match", list(match_map.keys()))
        match_id = match_map[selected_match]

        innings = st.radio("Innings", [1, 2])
        over = st.number_input("Over", min_value=0, max_value=50)
        ball = st.number_input("Ball (1-6)", min_value=1, max_value=6)

        player_names = [p[1] for p in players]
        batter = st.selectbox("Batter", player_names)
        bowler = st.selectbox("Bowler", player_names)
        runs = st.number_input("Runs", min_value=0, max_value=6)
        is_four = st.checkbox("Four")
        is_six = st.checkbox("Six")
        is_wicket = st.checkbox("Wicket")

        if st.button("Submit Ball"):
            add_ball_score(match_id, innings, over, ball, batter, bowler, runs, int(is_four), int(is_six), int(is_wicket))
            st.success("✅ Score recorded.")
    else:
        st.warning("⚠️ You need players and matches first.")

# Match Summary
elif menu == "Match Summary":
    st.subheader("📄 Match Summary")
    matches = get_matches()
    if matches:
        match_map = {f"Match #{m[0]} - {m[5]}": m[0] for m in matches}
        selected_match = st.selectbox("Select Match", list(match_map.keys()))
        match_id = match_map[selected_match]

        summary = get_match_summary(match_id)
        st.markdown(f"""
        - 🏏 Total Runs: `{summary['total_runs']}`
        - ❌ Wickets: `{summary['total_wickets']}`
        - 🎯 Fours: `{summary['total_fours']}`
        - 🎯 Sixes: `{summary['total_sixes']}`
        - 🔢 Balls: `{summary['balls']}`
        """)
    else:
        st.warning("No matches found.")

# Player Stats
elif menu == "Player Stats":
    st.subheader("📊 Player Stats")
    st.dataframe(get_player_stats())

# Export CSV
elif menu == "Export CSV":
    st.subheader("📄 Export Match CSV")
    matches = get_matches()
    if matches:
        match_map = {f"Match #{m[0]} - {m[5]}": m[0] for m in matches}
        selected_match = st.selectbox("Select Match", list(match_map.keys()))
        match_id = match_map[selected_match]

        if st.button("Export"):
            os.makedirs("exports", exist_ok=True)
            file_path = f"exports/match_{match_id}.csv"
            export_scores_to_csv(match_id, file_path)
            with open(file_path, 'rb') as f:
                st.download_button("Download CSV", f, file_name=f"match_{match_id}.csv")
    else:
        st.warning("No matches to export.")

# View Match Data
elif menu == "View Match Data":
    st.subheader("📋 Raw Scores")
    matches = get_matches()
    if matches:
        match_map = {f"Match #{m[0]} - {m[5]}": m[0] for m in matches}
        selected_match = st.selectbox("Select Match", list(match_map.keys()))
        match_id = match_map[selected_match]
        st.dataframe(get_scores_by_match(match_id))
    else:
        st.warning("No data available.")

# Reset
elif menu == "Reset":
    st.subheader("⚠️ Reset All Data")
    from modules.db import init_db
    if st.button("Delete All Data"):
        os.remove("cricket.db")
        init_db()
        st.success("🗑️ All data deleted and DB reset.")
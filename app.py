import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Data file paths
PLAYERS_FILE = 'players.json'
TEAMS_FILE = 'teams.json'
DRAFTS_FILE = 'drafts.json'

# Create drafts.json if it doesn't exist
if not os.path.exists(DRAFTS_FILE):
    with open(DRAFTS_FILE, 'w') as f:
        json.dump([], f)

# Helper functions
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_adps():
    """Calculate Average Draft Position for all players"""
    players = load_data(PLAYERS_FILE)
    drafts = load_data(DRAFTS_FILE)
    
    # Reset all ADPs to null
    for player in players:
        player['adp'] = None
    
    # If no drafts, just return the players
    if not drafts:
        return players
    
    # Calculate the draft positions
    player_positions = {}
    for draft in drafts:
        picks = draft.get('picks', [])
        for i, pick in enumerate(picks):
            player_id = pick.get('player_id')
            position = i + 1  # 1-indexed position
            
            if player_id not in player_positions:
                player_positions[player_id] = []
            
            player_positions[player_id].append(position)
    
    # Calculate average positions
    for player in players:
        player_id = player['player_id']
        if player_id in player_positions and player_positions[player_id]:
            positions = player_positions[player_id]
            player['adp'] = sum(positions) / len(positions)
    
    # Sort players by ADP (null values at the end)
    players.sort(key=lambda x: (x['adp'] is None, x['adp'] or float('inf')))
    save_data(PLAYERS_FILE, players)
    return players

def get_teams_with_players():
    """Get teams with captain and co-captain player details"""
    teams = load_data(TEAMS_FILE)
    players = load_data(PLAYERS_FILE)
    
    # Create player lookup dictionary
    player_lookup = {player['player_id']: player for player in players}
    
    for team in teams:
        if team['captain'] in player_lookup:
            team['captain_info'] = player_lookup[team['captain']]
        else:
            team['captain_info'] = {"name": "Unknown", "roles": []}
        
        team['co_captain_info'] = []
        for co_captain_id in team.get('co_captain', []):
            if co_captain_id in player_lookup:
                team['co_captain_info'].append(player_lookup[co_captain_id])
            else:
                team['co_captain_info'].append({"name": "Unknown", "roles": []})
    
    return teams

def get_draft_with_details(draft_key):
    """Get draft with team and player details"""
    drafts = load_data(DRAFTS_FILE)
    draft = next((d for d in drafts if d.get('draft_key') == draft_key), None)
    
    if not draft:
        return None
    
    players = load_data(PLAYERS_FILE)
    teams = load_data(TEAMS_FILE)
    
    # Create lookups
    player_lookup = {player['player_id']: player for player in players}
    team_lookup = {team['team_id']: team for team in teams}
    
    # Add player and team details to picks
    for pick in draft.get('picks', []):
        player_id = pick.get('player_id')
        team_id = pick.get('team_id')
        
        if player_id in player_lookup:
            pick['player_info'] = player_lookup[player_id]
        else:
            pick['player_info'] = {"name": "Unknown", "roles": []}
            
        if team_id in team_lookup:
            pick['team_info'] = team_lookup[team_id]
        else:
            pick['team_info'] = {"team_name": "Unknown"}
    
    return draft

def get_undrafted_players(draft_picks):
    """Get list of players not yet drafted in the current draft"""
    players = load_data(PLAYERS_FILE)
    teams = load_data(TEAMS_FILE)
    
    # Get IDs of players who are captains or co-captains
    captain_ids = [team.get('captain') for team in teams]
    co_captain_ids = []
    for team in teams:
        co_captain_ids.extend(team.get('co_captain', []))
    
    # All unavailable player IDs (captains, co-captains, and already drafted players)
    unavailable_ids = captain_ids + co_captain_ids + [pick.get('player_id') for pick in draft_picks]
    
    # Filter out unavailable players
    undrafted_players = [player for player in players if player['player_id'] not in unavailable_ids]
    
    # Sort by ADP (null values at the end)
    undrafted_players.sort(key=lambda x: (x['adp'] is None, x['adp'] or float('inf'), x['name']))
    
    return undrafted_players

def determine_next_pick(picks, teams):
    """Determine which team picks next based on snake draft logic"""
    if not picks:
        # First pick, team with pick_order=1 goes first
        return next((team for team in teams if team.get('pick_order') == 1), None)
    
    num_teams = len(teams)
    current_pick_number = len(picks)
    round_number = current_pick_number // num_teams + 1
    pick_in_round = current_pick_number % num_teams
    
    # In odd rounds (1, 3, 5...), teams pick in ascending order of pick_order
    # In even rounds (2, 4, 6...), teams pick in descending order of pick_order
    if round_number % 2 == 1:  # Odd round
        target_pick_order = pick_in_round + 1
    else:  # Even round
        target_pick_order = num_teams - pick_in_round
    
    return next((team for team in teams if team.get('pick_order') == target_pick_order), None)

# Route for home page
@app.route('/')
def home():
    players = load_data(PLAYERS_FILE)
    drafts = load_data(DRAFTS_FILE)
    
    # Sort players by ADP (null values at the end)
    players.sort(key=lambda x: (x['adp'] is None, x['adp'] or float('inf'), x['name']))
    
    return render_template(
        "index.html", 
        players=players, 
        drafts=drafts
    )

# API route to get all players
@app.route('/players', methods=['GET'])
def get_players():
    players = load_data(PLAYERS_FILE)
    return jsonify(players)

# API route to get undrafted players (excluding captains and co-captains)
@app.route('/undrafted_players/<draft_key>', methods=['GET'])
def get_available_players(draft_key):
    drafts = load_data(DRAFTS_FILE)
    draft = next((d for d in drafts if d.get('draft_key') == draft_key), None)
    
    picks = []
    if draft:
        picks = draft.get('picks', [])
    
    undrafted_players = get_undrafted_players(picks)
    return jsonify(undrafted_players)

# API route to get teams
@app.route('/teams', methods=['GET'])
def get_teams():
    teams = get_teams_with_players()
    return jsonify(teams)

# API route to get all drafts
@app.route('/drafts', methods=['GET'])
def get_drafts():
    drafts = load_data(DRAFTS_FILE)
    
    # Create summaries with only essential info
    draft_summaries = []
    for draft in drafts:
        draft_summaries.append({
            'draft_key': draft.get('draft_key'),
            'user_name': draft.get('user_name'),
            'picks_count': len(draft.get('picks', [])),
            'submitted_at': draft.get('submitted_at')
        })
    
    return jsonify(draft_summaries)

# API route to get a specific draft
@app.route('/drafts/<draft_key>', methods=['GET'])
def get_draft(draft_key):
    draft = get_draft_with_details(draft_key)
    
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404
    
    return jsonify(draft)

# API route to create a new draft
@app.route('/drafts/new', methods=['POST'])
def create_draft():
    data = request.json
    user_name = data.get('user_name')
    
    if not user_name:
        return jsonify({'error': 'User name is required'}), 400
    
    drafts = load_data(DRAFTS_FILE)
    
    # Check if user_name already exists
    if any(draft.get('user_name') == user_name for draft in drafts):
        return jsonify({'error': 'User name already exists. Please choose another.'}), 400
    
    # Create new draft
    draft_key = str(uuid.uuid4())
    new_draft = {
        'draft_key': draft_key,
        'user_name': user_name,
        'picks': [],
        'submitted_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    drafts.append(new_draft)
    save_data(DRAFTS_FILE, drafts)
    
    return jsonify({
        'draft_key': draft_key,
        'message': 'Draft created successfully. Please keep your draft key to edit later.'
    }), 201

# API route to update a draft
@app.route('/drafts/<draft_key>', methods=['PUT'])
def update_draft(draft_key):
    data = request.json
    picks = data.get('picks', [])
    
    if not isinstance(picks, list):
        return jsonify({'error': 'Picks must be an array'}), 400
    
    drafts = load_data(DRAFTS_FILE)
    draft_index = next((i for i, d in enumerate(drafts) if d.get('draft_key') == draft_key), None)
    
    if draft_index is None:
        return jsonify({'error': 'Draft not found'}), 404
    
    # Update the draft
    drafts[draft_index]['picks'] = picks
    drafts[draft_index]['submitted_at'] = datetime.utcnow().isoformat() + 'Z'
    
    save_data(DRAFTS_FILE, drafts)
    
    # Recalculate ADP
    calculate_adps()
    
    return jsonify({'message': 'Draft updated successfully'})

# Route for draft page
@app.route('/draft/<draft_key>')
def draft_page(draft_key):
    draft = get_draft_with_details(draft_key)
    
    if not draft:
        return redirect(url_for('home'))
    
    teams = get_teams_with_players()
    undrafted_players = get_undrafted_players(draft.get('picks', []))
    next_team = determine_next_pick(draft.get('picks', []), teams)
    
    return render_template(
        "draft.html",
        draft=draft,
        teams=teams,
        undrafted_players=undrafted_players,
        next_team=next_team
    )

# Route for view draft page (read-only)
@app.route('/view_draft/<draft_key>')
def view_draft_page(draft_key):
    draft = get_draft_with_details(draft_key)
    
    if not draft:
        return redirect(url_for('home'))
    
    teams = get_teams_with_players()
    
    return render_template(
        "view_draft.html",
        draft=draft,
        teams=teams
    )

if __name__ == "__main__":
    app.run(debug=True)
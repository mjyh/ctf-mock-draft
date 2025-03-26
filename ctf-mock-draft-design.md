# ctf-mock-draft-design.md

## 1. Background

This project is for creating a snake draft website for an online Capture the Flag (CTF) league (specifically “Infantry Online CTF”). Players have certain roles, teams have captains and co-captains, and the draft format is a snake order. We’re using simple HTML/CSS/JS for the front end and Flask + JSON for the backend.

### Main Features
- Users can **create** a new mock draft by providing a unique name. They receive a **draft key** to edit it later.
- Users can **edit** an existing draft by entering their draft key.
- Users can **view** any existing draft (read-only).
- The **home page** displays a list of drafts, current ADPs for all players, and links to create or edit a draft.

## 2. Requirements

1. **Snake Draft**:
   - We have multiple teams; in round 1 (odd), teams pick in ascending order of pick_order.
   - In round 2 (even), the order is reversed.
   - The front end calculates which team picks next based on the number of picks already made.

2. **Team Information**:
   - Stored in `teams.json` with fields:
     - `team_id`
     - `team_name`
     - `captain` (player ID)
     - `co_captain` (array of player IDs)
     - `pick_order` (1 for first, 2 for second, etc.)
   - On the draft page’s left pane, we show each team, its captain, co-captains, and the picks made so far.
   - Player names displayed on this pane include their **roles**.

3. **Players & Roles**:
   - `players.json` holds all players (including captains/co-captains).
   - Roles: O Inf, SG D Inf, CAW D Inf, O Hvy, D Hvy, SL, Med, Eng, Foot JT, Vehicle JT, Infiltrator.
   - Each role is displayed with a color-coded tag in the front end.
   - Each player object also includes an `adp` field, which may be `null` if not yet calculated.

4. **Mock Drafts**:
   - Stored in drafts.json. Each has:
     - draft_key (random string or UUID)
     - user_name (unique identifier)
     - picks (array of { team_id, player_id } in draft order)
     - submitted_at (timestamp)

5. **ADP Calculation**:
   - After each “Submit Draft,” we recalc every player’s average draft position from all stored drafts.
   - GET /players can return merged data with adp for each player.

---

## 3. Data Storage (JSON Files)

1. **players.json** (example):
```
   [
     {
       "player_id": 1,
       "name": "CaptainJohn",
       "roles": ["O Inf"]
     },
     {
       "player_id": 2,
       "name": "MedicMary",
       "roles": ["Med"]
     }
   ]
```
2. **teams.json** (example):
```
   [
     {
       "team_id": 101,
       "team_name": "Team Alpha",
       "captain": 1,
       "co_captain": 4,
       "pick_order": 1
     },
     {
       "team_id": 102,
       "team_name": "Team Bravo",
       "captain": 2,
       "co_captain": 5,
       "pick_order": 2
     }
   ]
```
3. **drafts.json** (example):
```
   [
     {
       "draft_key": "abcd-1234",
       "user_name": "DraftUser",
       "picks": [
         { "team_id": 101, "player_id": 7 },
         { "team_id": 102, "player_id": 3 }
       ],
       "submitted_at": "2025-03-25T12:34:56Z"
     }
   ]
```
---

## 4. Front-End Pages

### 4.1 Home Page
- Displays ADPs: A table or list of players sorted by ADP (or name if no ADP).
- Lists existing drafts: The user can select one to view (read-only).
- Create a Draft: Form to enter user_name → calls POST /drafts/new. If successful, returns draft_key.
- Edit a Draft: Form to enter a draft key, proceeds to the Draft Page if valid.

### 4.2 Draft Page
- Shows the draft key prominently with the message “KEEP THIS KEY TO EDIT LATER.”
- **Left Pane**:
  - Lists all teams in ascending `pick_order`.
  - Each team shows name, captain, co-captains, and picks so far.
  - Each player listed includes their **roles**.
- **Right Pane**:
  - Undrafted players, sorted by ADP or name.
  - Each shows name and **roles**.
  - Each has a button “Draft” to add that player as the next pick.
  - Single “Remove Last Pick” button to undo the most recent pick.
- “Submit Draft” button updates the server with the entire picks array.

### 4.3 Read-Only View Draft
- Similar layout as the Draft Page, but no buttons to change picks.
- The left pane shows the teams and all picks.
- The right pane can be disabled or just omitted.

---

## 5. Draft Flow

1. **Create**:
   - User enters user_name → POST /drafts/new returns a draft_key.
   - Goes to Draft Page, with a notice “KEEP THIS KEY.”

2. **Pick**:
   - Front end determines which team is up (snake logic) based on the length of picks.
   - User clicks “Draft” on a player → appended to the local picks array.

3. **Undo**:
   - User clicks “Remove Last Pick” → removes the last item in picks.

4. **Submit**:
   - User clicks “Submit Draft” → PUT /drafts/<draft_key> with the picks array, user_name.
   - Server saves to drafts.json, recalculates ADP.

---

## 6. ADP Calculation

- After PUT /drafts/<draft_key>, the server:
  - Reads all drafts in drafts.json.
  - For each draft’s picks, each index i is position i+1.
  - Computes each player’s average pick across all drafts.
  - Caches or stores this in memory so GET /players returns updated adp.

---

## 7. Color-Coded Roles

- O Inf → lighter red  
- SG D Inf, CAW D Inf → darker red  
- O Hvy → lighter blue  
- D Hvy → darker blue  
- Foot JT → light gray  
- Vehicle JT → dark gray  
- Med → yellow  
- Eng → orange-brown  
- Squad Leader → light green  
- Infiltrator → **purple**

---

## 8. Endpoints Summary

1. **POST /drafts/new**  
   Body: {"user_name": "..."}  
   Returns: {"draft_key": "..."} plus a message.  
   Enforce user_name uniqueness.

2. **PUT /drafts/<draft_key>**  
   Overwrites the picks for that draft, updates submitted_at, recalculates ADP.

3. **GET /drafts**  
   Returns a list of summaries (draft_key, user_name, picks_count, etc.).

4. **GET /drafts/<draft_key>**  
   Returns the full draft object for that key (if the user wants to reload picks).

5. **GET /players**  
   Returns all players, each with an adp field if available.

6. **GET /teams**  
   Returns teams.json data (team_id, name, captain, co_captain, pick_order).

---

## 9. Summary

- **Home Page**: Show current ADPs, list drafts, let user create/edit drafts.
- **Draft Page**: Show the draft key, teams with picks on the left, undrafted players on the right, plus submit/undo/delete controls.
- **View Draft**: Read-only mode for an existing draft.
- **Server**: JSON-based, a few simple endpoints for managing drafts and computing ADPs.
# ctf-mock-draft-design.md

## 1. Background

This project is for creating a mock-draft website for an online Capture the Flag (CTF) league (specifically “Infantry Online CTF”). Each team typically drafts 15–19 players, with only 10 players active in a match. Each player can handle certain roles (Offense Infantry, Defense Infantry, Medic, Engineer, etc.).

We want a simple web app where:
- Users can log in, select the CTF league (CTFDL Season 4).
- They can view a list of players (with roles) and build a mock draft.
- After submitting, each draft is stored and contributes to average draft positions (ADP) of players.
- The available player list is dynamically sorted by ADP for future drafts.
- Users can revisit their draft (via a key generated for them) to edit or resubmit.
- An admin user can delete or moderate drafts.

The technology focus is minimal overhead, likely **Flask** (Python) or another lightweight approach, storing data either in JSON files or a simple SQLite database. We plan to host it on a service like PythonAnywhere or Render.

---

## 2. Requirements

1. **User Accounts & Authentication**  
   - Ability to **sign up** (username/password) and **log in**.  
   - Maintain user sessions or tokens.  

2. **Mock Draft Creation**  
   - Users choose the current league (e.g., “CTFDL Season 4”).  
   - A list of **all players** (name, possible roles) is displayed.  
   - Users draft ~15–19 players (with only 10 as “starters” in a real game, but that detail can be noted).  
   - After picking players, they **submit** the draft.

3. **Data Storage**  
   - Store player info in a file or table (e.g. `players.json` or a `players` table).  
   - Store drafts (`drafts.json` or a `drafts` table).  
   - Store user accounts (`users.json` or a `users` table).  
   - Optionally store team captains, co-captains, etc.  

4. **ADP (Average Draft Position)**  
   - Each time a user loads the list of players, they are sorted by ADP.  
   - ADP = average pick index across all submitted drafts (ex. if a player is picked 1st, 5th, and 3rd in three different drafts, their ADP is (1+5+3)/3 = 3.0).  
   - If no data, sort players alphabetically or by some default method.

5. **Editing Drafts**  
   - Users can come back (via login or a unique “draft key”) to modify picks.  
   - Only the latest submitted version from a user should count for ADP, or we keep all drafts—this can be decided in the implementation.

6. **Admin Controls**  
   - An admin account can view all drafts and **delete** or **remove** them if needed.

7. **Deployment**  
   - Low-bloat environment, such as Flask on PythonAnywhere or Render.  
   - Must handle basic concurrency (multiple users drafting).  
   - JSON-based or SQLite-based storage should be enough for a small user base.

---

## 3. Proposed Design

### 3.1 Overall Architecture

- **Front End**:  
  - Minimal HTML/CSS/JS or a small framework like Vue/React (optional).  
  - Displays pages: *Login*, *Sign Up*, *Draft*, *Admin Panel*.  
  - Interacts with backend via REST endpoints (JSON).

- **Backend (Flask)**:  
  - Routes for sign up, log in, creating/fetching drafts, listing players, admin actions.  
  - Data stored in JSON files or a small SQLite database.  
  - Logic for ADP computation triggered on each read or after each draft submission.

- **Data Store**:  
  - **JSON Option**: `players.json`, `users.json`, `drafts.json`.  
  - **SQLite Option**: tables `players`, `users`, `drafts`, with a simple schema.

### 3.2 Endpoint Sketch (RESTful)

1. **Authentication**  
   - `POST /signup`: Create new user (store hashed password).  
   - `POST /login`: Validate credentials, set session/cookie or return a token.

2. **Players**  
   - `GET /players`: Returns all players sorted by ADP. (Backend calculates ADP on the fly or has a cached value.)

3. **Drafts**  
   - `GET /drafts`: Returns the current user’s existing drafts.  
   - `POST /drafts`: Creates a new draft. Body includes `league`, `picks` (list of player IDs).  
   - `PUT /drafts/<draft_id>`: Edits an existing draft.  
   - `DELETE /drafts/<draft_id>`: Owner or admin can delete a draft.

4. **Admin**  
   - `GET /admin/drafts`: Return all drafts (admin only).  
   - `DELETE /admin/drafts/<draft_id>`: Delete any user’s draft (admin only).

### 3.3 Data Model (JSON Example)

- **`players.json`**:
  ```json
  [
    { "player_id": 1, "name": "PlayerA", "roles": ["O Inf", "Medic"] },
    { "player_id": 2, "name": "PlayerB", "roles": ["D Inf", "Engineer"] },
    ...
  ]

# CTF Mock Draft Development Guidelines

## Build & Run Commands
- Run the application: `python app.py`
- Run development server with debug: `flask run --debug`

## Important Notes
- NEVER run the server after making code changes (don't run python app.py or flask run)
- NEVER automatically add or commit changes with git - wait for explicit instruction to commit
- Do not add explanatory messages or summaries after listing changes

## UI Design
- Color scheme: Dark gray background (#212121) with gold accents (#d4af37)
- Banner layout: Draft key (flex: 2), Remove button (flex: 1.5), Submit button (flex: 1.5), Round display (flex: 1), Pick display (flex: 1), Team display (flex: 2)
- Team cards should be arranged in a horizontal row with equal spacing
- Player cards use clear spacing with role tags for better visibility

## Setup
- Install dependencies: `pip install -r requirements.txt`
- Create virtual environment: `python -m venv venv`
- Activate virtual environment: 
  - Unix/MacOS: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`

## Code Style
- Follow PEP 8 for Python code style (https://peps.python.org/pep-0008/)
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 79 characters
- Use snake_case for functions, variables, and modules
- Use CamelCase for classes
- Use docstrings for documenting functions/classes
- Import order: standard library, third-party, local modules
- Error handling: use try/except blocks with specific exceptions
- Type hinting: use Python's typing module for function annotations
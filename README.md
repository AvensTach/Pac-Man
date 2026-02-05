# Pac-Man (Python / Pygame)

Overview
\- A small Pac\-Man inspired project implemented in Python using Pygame.  
\- Focused on grid/tile\-based ghost movement (smooth pixel transitions tile\-by\-tile). Useful as a learning project for classic arcade movement and simple AI.

Status
\- Work in progress. Core ghost tile\-based movement is implemented. Player movement, full AI behaviors, and complete level assets may be partial or under development.

Features
\- Tile\-based ghost movement: ghosts decide direction only at tile centers and traverse one tile at a time with smooth pixel motion.  
\- Level abstraction: `level.py` exposes `is_wall` for collision checks and map queries.  
\- Configurable constants in `settings.py` (e.g., `TILE_SIZE`, `BASE_SPEED`, rows/cols).  

Quick start (Windows)
1. Install Python 3.11+ if not already installed.  
2. Create and activate a virtual environment (recommended):
   - `python -m venv venv`
   - `venv\Scripts\activate`
3. Install dependencies:
   - `pip install pygame`
4. Run the game from the project root:
   - `python main.py`
5. Or open the project in PyCharm (`PyCharm 2025.3.2.1`) and run `main.py`.

Controls
\- Depends on current project implementation. If a player is implemented, typical controls are arrow keys for movement. Check `main.py` for exact input handling.

Project layout
\- `Pac-Man/` (project root)
  - `main.py` \- entry point / game loop
  - `ghosts.py` \- ghost entity and tile\-based movement logic
  - `level.py` \- level map, `is_wall` and tile helpers
  - `settings.py` \- constants (TILE_SIZE, BASE_SPEED, ROWS, COLS, enums)
  - `sprites/GeneralSprites.png` \- sprite sheet (not required for rectangle placeholder rendering)
  - `README.md` \- this file
  - `PRD.md`, `LICENSE` etc.

Configuration & tuning
\- Adjust `settings.py` values to change gameplay feel:
  - `TILE_SIZE` controls grid cell pixel size.
  - `BASE_SPEED` controls pixels per frame; tile traversal time = `TILE_SIZE / BASE_SPEED` frames.
  - `ROWS` / `COLS` set map dimensions.
\- Ghosts use `Level.is_wall(row, col)` before starting a tile move and wrap edges using modulo semantics.

Developer notes
\- Ghost AI is currently simple/random. Recommended improvements:
  - Direction priority to avoid unnecessary reversals.
  - Implement ghost personalities (chase/scatter/ambush/frightened).
  - Add player tile\-based movement matching ghosts so turns happen at tile centers.
  - Replace rectangle drawing with sprite rendering using `sprites/GeneralSprites.png`.
\- Unit tests can verify that ghosts never occupy wall tiles and wrap correctly.

License
\- See `LICENSE` in project root.

Contact / Credits
\- Project maintained by the repository owner and his team. See Git history for authorship.

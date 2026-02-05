# Product Requirements Document (PRD)

| **Project Name** | Pac-Man Clone (Python) |
|:-----------------|:-----------------------|
| **Version**      | 1.0                    |
| **Status**       | Draft / In-Development |
| **Authors**      | TBD                    |

---

## 1. Executive Summary
The goal of this project is to develop a functional clone of the arcade classic **Pac-Man** using the Python programming language. The project aims to demonstrate proficiency in object-oriented programming (OOP), game loop architecture, and algorithm implementation (specifically for Ghost AI). The final product will be a playable 2D game where the user controls Pac-Man to eat pellets while avoiding ghosts in a maze.

## 2. Project Scope

### 2.1 In-Scope
* **Core Gameplay:** Player movement, collision detection, score tracking.
* **Entities:** Pac-Man, 4 Ghosts (Red, Pink, Cyan, Orange), Pellets, Power Pellets.
* **AI:** Basic pathfinding and state behavior for ghosts (Chase, Scatter, Frightened).
* **UI:** Start Screen, HUD (Score, Lives), Game Over Screen.
* **Audio:** Basic sound effects (waka-waka, death, eating fruit).

### 2.2 Out-of-Scope (MVP)
* Online multiplayer.
* Complex procedurally generated maps (fixed map will be used).
* Save/Load game state functionality (persisting high scores to a text file is optional).
* Mobile/Touch controls.

---

## 3. User Stories
* **As a Player**, I want to move Pac-Man up, down, left, and right using the arrow keys so that I can navigate the maze.
* **As a Player**, I want to earn points by collecting pellets so that I can achieve a high score.
* **As a Player**, I want to see my current score and remaining lives displayed on the screen.
* **As a Player**, I want the game to become harder as I progress (or have ghosts with distinct behaviors) to keep the gameplay engaging.
* **As a Player**, I want to be able to pause or restart the game easily.

---

## 4. Functional Requirements

### 4.1 Game Mechanics
* **Movement:** Pac-Man must move continuously in the chosen direction until he hits a wall or the player changes direction. Movement is grid-based.
* **Collision Detection:**
    * **Wall:** Stop movement.
    * **Pellet:** Remove pellet, increase score (+10), play sound.
    * **Power Pellet:** Remove pellet, increase score (+50), change Ghost state to "Frightened."
    * **Ghost (Normal):** Pac-Man loses a life; positions reset.
    * **Ghost (Frightened):** Ghost is eaten, eyes return to spawn, score increases (+200/400/800/1600).
* **Win Condition:** All pellets on the map are consumed. Level resets (potentially with increased speed).
* **Lose Condition:** Player lives reach 0.



### 4.2 Ghost AI Behaviors
The ghosts must implement distinct targeting logic (if advanced) or random movement (if basic MVP):
1.  **Blinky (Red):** Directly chases Pac-Man's current tile.
2.  **Pinky (Pink):** Targets 4 tiles in front of Pac-Man (ambush).
3.  **Inky (Cyan):** Relies on Blinky’s position (flanking).
4.  **Clyde (Orange):** Chases Pac-Man but retreats to his corner when too close.

### 4.3 User Interface (UI)
* **Main Menu:** Title graphic, "Press Enter to Start" prompt.
* **In-Game HUD:**
    * Top Left: "SCORE: [Value]"
    * Top Right: "HIGH SCORE: [Value]"
    * Bottom Left: Life icons (Pac-Man sprites).
* **Game Over:** "GAME OVER" text overlay and option to restart.

---

## 5. Non-Functional Requirements
* **Performance:** The game must run at a consistent **60 FPS** on standard university lab computers.
* **Code Quality:** Code must adhere to **PEP 8** standards.
* **Architecture:** Must utilize **Object-Oriented Programming (OOP)**. Separate classes for `Game`, `Player`, `Ghost`, and `Map`.
* **Library:** The project will use `pygame` for rendering.

---

## 6. Technical Architecture

### 6.1 Tech Stack
* **Language:** Python 3.11+
* **Graphics Library:** Pygame (Recommended for sprite handling and sound)
* **IDE:** VS Code / PyCharm

### 6.2 Proposed Class Structure
* `main.py`: Entry point, handles the game loop.
* `settings.py`: Constants (Colors, Screen Dimensions, FPS, etc.).
* `class Player`: Handles input parsing, movement vectors, and animation frames.
* `class Ghost`: Handles AI states (Scatter/Chase/Frightened) and pathfinding algorithms (A* or Euclidean distance).
* `class Level`: Loads the map layout (often from a 2D array or text file).



---

## 7. Milestones & Timeline

| Phase      | Description                                                        |
| :--------- | :----------------------------------------------------------------- |
| **Phase 1** | Project Setup, Git Repo init, Basic Window & Map rendering.       |
| **Phase 2** | Pac-Man Movement & Wall Collision.                                |
| **Phase 3** | Pellet Collection & Scoring System.                               |
| **Phase 4** | Ghost Implementation (Basic Movement).                            |
| **Phase 5** | Ghost AI & Collision Logic (Win/Loss states).                     |
| **Phase 6** | UI, Sound, Polish, and Bug Fixing.                                |
---

## 8. Future Improvements (Post-Submission)
* Implementation of the original "fruit" mechanics for bonus points.
* Adding a pathfinding visualizer (debug mode) to show Ghost logic.
* Controller support using `pygame.joystick`.
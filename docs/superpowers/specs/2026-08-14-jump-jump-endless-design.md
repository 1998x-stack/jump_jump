# Design: "Jump Jump" Endless Jumper (fixed prototype)

## Goal

Turn the current single-static-platform prototype into a minimal, playable
Doodle-Jump-style endless jumper: the player bounces upward onto platforms,
the world scrolls as they climb, score grows with height, and falling off the
bottom ends the game.

## Gameplay Loop

- The player always falls under gravity.
- Landing on a platform **auto-bounces** the player upward (Doodle Jump style).
  No jump input is required.
- The only player input is horizontal steering: **← / right (or A/D)**, clamped
  to the screen edges.
- Camera scrolls the world downward as the player climbs, so new platforms
  constantly appear above and stale ones disappear below — endless climbing.
- **Score = max height reached**, rendered top-left.
- Falling below the bottom edge triggers **game over**.

## Architecture

Built on the existing module structure.

### `config.py`
Add tunable constants; keep existing ones:
- `PLAYER_SPEED` (horizontal velocity)
- `BOUNCE_VELOCITY` (upward velocity on platform landing)
- `SHIFT_THRESHOLD` (fraction of screen height at which camera scrolls)
- `PLATFORM_MIN_GAP` / `PLATFORM_MAX_GAP` (reachable vertical gap range)
- `SCROLL_OFFSET` (how far platforms shift per camera scroll), or derive from
  player velocity.
- Keep the existing `GRAVITY` value.
- Colors for platform/player remain configurable (move the two hardcoded colors
  out of the classes into `config.py`).

### `player.py`
- `update(self)`: always applies gravity (`vel_y += GRAVITY`); horizontal
  velocity from held keys; clamps to screen width.
- Auto-bounce: on landing while `vel_y > 0`, set `vel_y = -BOUNCE_VELOCITY`
  instead of the current stop-on-top behavior.
- Tracks `max_height` (world-coordinate height reached) for scoring.

### `jump_platform.py`
- `Platform` stays a static rectangle placed at a given world position.
- New platform **generator** logic:
  - `generate_platforms(platforms, top_world_y, ...)` spawns static platforms at
    random x with vertical gaps between `PLATFORM_MIN_GAP` and `PLATFORM_MAX_GAP`
    so each is reachable from the one below.
  - Initial setup builds a column of platforms from the bottom of the screen to
    the top.
  - During play, platforms are spawned above the visible top and removed from the
    list once they scroll below the bottom.

### `game_functions.py`
- `check_events`: replace mouse hold-to-jump with `KEYDOWN`/`KEYUP`:
  - `K_left`/`K_a` and `K_right`/`K_d` set/unset horizontal movement.
  - `K_space` triggers restart when in game-over state.
- `update_screen`: handle camera scroll, platform generation/despawn, score
  update, and render (player, platforms, score).

### `main.py`
- Three-state loop:
  - `playing` — update + render each frame.
  - `game_over` — freeze player, show "Game Over — Score: N — press SPACE".
  - (SPACE transition `game_over -> playing`, resetting to initial state.)
- Set window caption; remove the no-op score block (score now owned by
  update/render flow).

## World Scrolling

- Draw platforms/player in screen space; shift platform screen position by the
  scroll delta each frame once the player passes `SHIFT_THRESHOLD * screen height`.
- The player's screen position can stay fixed near the threshold as the camera
  rises.
- Score derives from the player's **world height** (increases monotonically).

## Game Over & Restart

- If player's top passes `SCREEN_HEIGHT` (below bottom), trigger `game_over`.
- Restart on SPACE resets platforms, player, score, and camera to the initial
  state.

## Visuals (minimal)

- Keep colored rectangles: green player (`config.py`), red platform.
- `assets/images/*.png` and `jump.wav` are **not** wired in this change (future
  work).

## Out of Scope (YAGNI)

- Moving / disappearing platforms.
- Mouse / touch-input.
- Audio playback.
- Using the `.png` assets.
- `requirements.txt` / `README.md` packaging (noted but deferred).

## Success Criteria

- Player can accelerate continuously, climbing past several newly spawned
  platforms with left/right steering.
- Score increments with height and is displayed.
- Falling past the bottom edge ends the game and allows restart with SPACE.
- No `is_jumping`/`press_time` logic remains (removed).
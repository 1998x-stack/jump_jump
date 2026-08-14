# Jump Jump Endless Jumper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-static-platform pygame prototype into a playable Doodle-Jump-style endless jumper with auto-bounce, keyboard steering, scrolling platforms, climbing score, and game-over/restart.

**Architecture:** Reuse the existing `config → player → platform → game_functions → main` structure. Player always falls under gravity and auto-bounces off platforms; platforms are generated upward from a random `x` at reachable vertical gaps; a camera scrolls the world down as the player climbs past a threshold; score accumulates from scroll; falling below the screen triggers game over with SPACE restart.

**Tech Stack:** Python 3, pygame. Tests via `pytest` with a headless (`SDL_VIDEODRIVER=dummy`) setup so no display is needed.

## Global Constraints

- Only keyboard input: `←`/`A` (left), `→`/`D` (right), `SPACE` (restart on game over). No mouse.
- The player always falls under gravity; jumping is an automatic bounce on platform contact. No jump input.
- Horizontal position clamps to `[0, SCREEN_WIDTH]`.
- Gravity always `GRAVITY = 0.5` (unchanged from spec).
- New constants `PLAYER_COLOR`, `PLATFORM_COLOR`, `PLAYER_SPEED`, `BOUNCE_VELOCITY`, `SHIFT_THRESHOLD`, `PLATFORM_MIN_GAP`, `PLATFORM_MAX_GAP` live in `config.py`.
- `assets/images/*.png` and `assets/sounds/jump.wav` are NOT wired in this change.
- No `is_jumping` / `press_time` / hold-to-jump logic may remain anywhere.
- Each task ends with a passing test suite and a commit.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `config.py` | All constants; game feel tunables |
| `player.py` | Player physics: gravity, horizontal motion, auto-bounce collision |
| `jump_platform.py` | `Platform` class + platform generator/prune functions |
| `game_functions.py` | `check_events` (keyboard), `update_screen` (scroll, gen, render) |
| `main.py` | Game loop, score accumulation, game-over/restart state machine |
| `tests/conftest.py` | Headless pygame fixture |
| `tests/test_player.py` | Player physics tests |
| `tests/test_platform.py` | Platform generator tests |

---

### Task 1: Player Physics (gravity, horizontal, auto-bounce)

**Files:**
- Modify: `config.py`
- Rewrite: `player.py`
- Create: `tests/conftest.py`
- Create: `tests/test_player.py`

**Interfaces:**
- Consumes: `PLAYER_SIZE`, `PLAYER_START_POS`, `GRAVITY`, `PLAYER_COLOR`, `PLAYER_SPEED`, `BOUNCE_VELOCITY`, `SCREEN_WIDTH` from config.
- Produces (later tasks rely on these exact names):
  - `Player()` with attributes `image`, `rect`, `vel_y` (float), `direction` (int, -1/0/+1).
  - `Player.update()` → applies gravity to `vel_y` and `rect.y`.
  - `Player.move_horizontal()` → moves by `direction * PLAYER_SPEED`, clamps to screen.
  - `Player.collide(platform)` → returns `True` and sets `vel_y = BOUNCE_VELOCITY` + snaps `rect.bottom = platform.rect.top` on a downward landing; else returns `False`.
  - `Player.draw(screen)`.

- [ ] **Step 1: Add player constants to `config.py`**

Append to `config.py`:

```python
# Player turns
PLAYER_COLOR = (0, 255, 0)
PLAYER_SPEED = 6
BOUNCE_VELOCITY = -14
```

Keep existing `GRAVITY = 0.5` and `PLAYER_SIZE`, `PLAYER_START_POS`.

- [ ] **Step 2: Create headless test scaffolding** `tests/conftest.py`

```python
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
import pytest


@pytest.fixture(autouse=True)
def pygame_setup():
    pygame.init()
    yield
    pygame.quit()
```

- [ ] **Step 3: Write the failing tests** `tests/test_player.py`

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
from config import GRAVITY, PLAYER_SPEED, BOUNCE_VELOCITY, SCREEN_WIDTH
from player import Player


def make_platform(top, left=0, width=100, height=20):
    img = pygame.Surface((width, height))
    rect = img.get_rect()
    rect.topleft = (left, top)
    return SimpleNamespace(rect=rect)


from types import SimpleNamespace


def test_gravity_applies_when_moving():
    p = Player()
    p.vel_y = 0.0
    before_y = p.rect.y
    p.update()
    assert p.vel_y == GRAVITY
    assert p.rect.y > before_y


def test_horizontal_move_right():
    p = Player()
    p.direction = 1
    before_x = p.rect.x
    p.move_horizontal()
    assert p.rect.x == before_x + PLAYER_SPEED


def test_horizontal_clamped_to_left():
    p = Player()
    p.rect.left = 0
    p.direction = -1
    p.move_horizontal()
    assert p.rect.left == 0


def test_horizontal_clamped_to_right():
    p = Player()
    p.rect.right = SCREEN_WIDTH
    p.direction = 1
    p.move_horizontal()
    assert p.rect.right == SCREEN_WIDTH


def test_bounce_on_landing():
    p = Player()
    p.vel_y = 10
    p.rect.bottom = 100
    plat = SimpleNamespace(rect=pygame.Rect(0, 100, 100, 20))
    assert p.collide(plat) is True
    assert p.vel_y == BOUNCE_VELOCITY
    assert p.rect.bottom == plat.rect.top


def test_no_bounce_when_moving_up():
    p = Player()
    p.vel_y = -5
    plat = SimpleNamespace(rect=pygame.Rect(0, 100, 100, 20))
    assert p.collide(plat) is False


def test_no_bounce_when_approaching_from_side():
    p = Player()
    p.vel_y = 100
    plat = SimpleNamespace(rect=pygame.Rect(500, 100, 100, 20))
    # previous frame bottom was already below platform top -> side hit, no bounce
    p.rect.bottom = plat.rect.top + 5
    assert p.collide(plat) is False
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/test_player.py -v`
Expected: FAIL — `ImportError / AttributeError` (`player.init` creates old surface, `collide` undefined).

- [ ] **Step 5: Implement `player.py`**

```python
# player.py

import pygame
from config import (PLAYER_SIZE, PLAYER_START_POS, GRAVITY, PLAYER_COLOR,
                    PLAYER_SPEED, BOUNCE_VELOCITY, SCREEN_WIDTH)


class Player:
    def __init__(self):
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = PLAYER_START_POS
        self.vel_y = 0.0
        self.direction = 0

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

    def move_horizontal(self):
        self.rect.x += self.direction * PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def collide(self, platform):
        if (self.vel_y > 0 and self.rect.colliderect(platform.rect)
                and self.rect.bottom - self.vel_y <= platform.rect.top):
            self.vel_y = BOUNCE_VELOCITY
            self.rect.bottom = platform.rect.top
            return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_player.py -v`
Expected: 7 passed.

- [ ] **Step 7: Commit**

```bash
git add config.py player.py tests/conftest.py tests/test_player.py
git commit -m "feat: player auto-bounce physics with horizontal steering"
```



---

### Task 2: Platform Class + Generator

**Files:**
- Modify: `config.py`
- Rewrite: `jump_platform.py`
- Create: `tests/test_platform.py`

**Interfaces:**
- Consumes: `PLATFORM_SIZE`, `PLATFORM_COLOR`, `PLATFORM_MIN_GAP`, `PLATFORM_MAX_GAP`, `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `random`.
- Produces (later tasks rely on these exact signatures):
  - `Platform(x, y)` — attributes `image`, `rect` (topleft = `(x, y)`), `draw(screen)`.
  - `generate_initial_platforms() -> list[Platform]` — builds a column from near the bottom up past the top of the viewport; gaps in `[PLATFORM_MIN_GAP, PLATFORM_MAX_GAP]`.
  - `refill_platforms(platforms)` — mutates list, keeps appending above until the newest platform reaches `rect.top <= 0`.
  - `remove_platforms_below(platforms, bottom)` — mutates list, drops any platform with `rect.top > bottom`.

- [ ] **Step 1: Add platform constants to `config.py`**

```python
# Platform settings
PLATFORM_COLOR = (255, 0, 0)
PLATFORM_MIN_GAP = 60
PLATFORM_MAX_GAP = 120
```

Keep `PLATFORM_SIZE = (100, 20)`.

- [ ] **Step 2: Write the failing tests** `tests/test_platform.py`

```python
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (PLATFORM_MIN_GAP, PLATFORM_MAX_GAP, SCREEN_WIDTH,
                    PLATFORM_SIZE, SCREEN_HEIGHT)
from jump_platform import (generate_initial_platforms, refill_platforms,
                           remove_platforms_below)


def test_initial_platforms_reach_above_screen():
    platforms = generate_initial_platforms()
    assert platforms
    tops = sorted(p.rect.top for p in platforms)
    assert tops[0] <= 0                  # highest reaches the top
    assert tops[-1] >= SCREEN_HEIGHT - 150  # bottom is near the start zone


def test_initial_gaps_within_reachable_range():
    platforms = generate_initial_platforms()
    for a, b in zip(platforms, platforms[1:]):
        gap = a.rect.top - b.rect.top   # a = lower, b = higher (list order)
        assert PLATFORM_MIN_GAP <= gap <= PLATFORM_MAX_GAP


def test_platforms_inside_horizontal_bounds():
    for p in generate_initial_platforms():
        assert p.rect.left >= 0
        assert p.rect.right <= SCREEN_WIDTH


def test_refill_extends_to_top():
    platforms = generate_initial_platforms()

    # lower everything by a big scroll (simulate world moving down)
    for p in platforms:
        p.rect.y += 400
    assert min(p.rect.top for p in platforms) > 0
    refill_platforms(platforms)
    assert min(p.rect.top for p in platforms) <= 0
    for a, b in zip(platforms, platforms[1:]):
        gap = a.rect.top - b.rect.top
        assert PLATFORM_MIN_GAP <= gap <= PLATFORM_MAX_GAP


def test_remove_platforms_below_screen():
    platforms = generate_initial_platforms()
    below_count = 0
    for i, p in enumerate(platforms):
        if p.rect.top > SCREEN_HEIGHT:
            below_count += 1
    remove_platforms_below(platforms, SCREEN_HEIGHT)
    assert all(p.rect.top <= SCREEN_HEIGHT for p in platforms)
    assert len(platforms) == len(platforms)  # only ones behind end removed
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_platform.py -v`
Expected: FAIL — `ModuleNotFoundError` for the new functions.

- [ ] **Step 4: Implement `jump_platform.py`**

```python
# jump_platform.py

import random
import pygame
from config import (PLATFORM_SIZE, PLATFORM_COLOR, PLATFORM_MIN_GAP,
                    PLATFORM_MAX_GAP, SCREEN_WIDTH, SCREEN_HEIGHT)


class Platform:
    def __init__(self, x, y):
        self.image = pygame.Surface(PLATFORM_SIZE)
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def _random_x():
    return random.randint(0, SCREEN_WIDTH - PLATFORM_SIZE[0])


def _next_y(top):
    return top - random.randint(PLATFORM_MIN_GAP, PLATFORM_MAX_GAP)


def generate_initial_platforms():
    platforms = [Platform(_random_x(), SCREEN_HEIGHT - 150)]
    while platforms[-1].rect.top > 0:
        platforms.append(Platform(_random_x(), _next_y(platforms[-1].rect.top)))
    return platforms


def refill_platforms(platforms):
    if not platforms:
        platforms.append(Platform(_random_x(), SCREEN_HEIGHT - 150))
    while platforms[-1].rect.top > 0:
        platforms.append(Platform(_random_x(), _next_y(platforms[-1].rect.top)))


def remove_platforms_below(platforms, screen_height):
    for p in list(platforms):
        if p.rect.top > screen_height:
            platforms.remove(p)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_platform.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A config.py jump_platform.py tests/test_platform.py
git commit -m "feat: platform generation and prune helpers"
```

---

### Task 3: Game Loop Integration (keyboard, scroll, score, game over)

**Files:**
- Rewrite: `game_functions.py`
- Rewrite: `main.py`
- Modify: `config.py` (add SHIFT_THRESHOLD)

**Interfaces:**
- Consumes: Task 1 `Player` API, Task 2 `Platform`/generator API.
- Produces (later tasks rely on these):
  - `check_events(player) -> str | None` — returns `"quit"` never returns; returns `"restart"` on SPACE press; handles `KEYDOWN`/`KEYUP` for direction.
  - `update_screen(screen, player, platforms) -> int` — renders, updates, scrolls; returns the scroll delta (positive int) so caller can accumulate score.
  - `main.run_game()` — the whole game.

- [ ] **Step 1: Add scroll threshold to `config.py`**

```python
# Camera
SHIFT_THRESHOLD = 150   # px from top where the camera starts scrolling
```

- [ ] **Step 2: Write the failing integration tests**

Create `tests/test_game_functions.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
import pytest
from config import SCREEN_HEIGHT, SHIFT_THRESHOLD, WHITE
from player import Player
from jump_platform import generate_initial_platforms
import game_functions as gf


def test_update_screen_scrolls_when_player_high():
    screen = pygame.display.set_mode((10, 10))
    player = Player()
    platforms = generate_initial_platforms()
    player.rect.top = 0                     # too high -> must scroll
    scroll = gf.update_screen(screen, player, platforms)
    assert scroll > 0
    assert player.rect.top == SHIFT_THRESHOLD


def test_update_screen_no_scroll_when_below_threshold():
    screen = pygame.display.set_mode((10, 10))
    player = Player()
    player.rect.top = SHIFT_THRESHOLD + 50
    platforms = generate_initial_platforms()
    scroll = gf.update_screen(screen, player, platforms)
    assert scroll == 0
```

- [ ] **Step 3: Run the integration tests to verify they fail**

Run: `pytest tests/test_game_functions.py -v`
Expected: fail (`update_screen` does not exist / no scroll behavior).

- [ ] **Step 4: Implement `game_functions.py`**

```python
# game_functions.py

import sys

import pygame
from config import (SCREEN_HEIGHT, SHIFT_THRESHOLD, WHITE)
from player import Player
from jump_platform import refill_platforms, remove_platforms_below


def check_events(player):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                player.direction = -1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                player.direction = 1
            elif event.key == pygame.K_SPACE:
                return "restart"
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a) and player.direction == -1:
                player.direction = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and player.direction == 1:
                player.direction = 0
    return None


def update_screen(screen, player, platforms):
    screen.fill(WHITE)

    player.move_horizontal()
    player.update()
    for platform in platforms:
        player.collide(platform)

    scroll = 0
    if player.rect.top < SHIFT_THRESHOLD:
        scroll = SHIFT_THRESHOLD - player.rect.top
        player.rect.top = SHIFT_THRESHOLD
        for platform in platforms:
            platform.rect.y += scroll

    refill_platforms(platforms)
    remove_platforms_below(platforms, SCREEN_HEIGHT)

    for platform in platforms:
        platform.draw(screen)
    player.draw(screen)

    return scroll
```

- [ ] **Step 5: Run integration tests to verify they pass**

Run: `pytest tests/test_game_functions.py -v`
Expected: PASS.

- [ ] **Step 6: Implement `main.py`**

```python
# main.py

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from player import Player
from jump_platform import generate_initial_platforms
import game_functions as gf


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jump Jump")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    state = "playing"
    score = 0
    platforms = generate_initial_platforms()
    player = Player()

    while True:
        clock.tick(FPS)
        action = gf.check_events(player)

        if action == "restart" and state == "game_over":
            state = "playing"
            score = 0
            platforms = generate_initial_platforms()
            player = Player()

        if state == "playing":
            scroll = gf.update_screen(screen, player, platforms)
            score += scroll
            score_surface = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_surface, (10, 10))
            if player.rect.top > SCREEN_HEIGHT:
                state = "game_over"
        else:
            screen.fill(WHITE)
            over = font.render(f"Game Over - Score: {score}", True, (0, 0, 0))
            prompt = font.render("Press SPACE to restart", True, (0, 0, 0))
            cx = SCREEN_WIDTH // 2
            screen.blit(over, (cx - over.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(prompt, (cx - prompt.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()


if __name__ == "__main__":
    run_game()
```

- [ ] **Step 7: Smoke-test the full app** (needs a window; run with a timeout)

Run: `timeout 3 python main.py; echo "exit: $?"`
Expected: starts without exceptions (timeout exit code 124 or hand-run manually).

- [ ] **Step 8: Run full test suite**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add game_functions.py main.py config.py tests/test_game_functions.py
git commit -m "feat: endless scrolling gameplay with keyboard controls and game over"
```

---

### Task 4: Final Verification & Cleanup

**Files:**
- Verify: all files
- Create: none

**Interfaces:** none new.

- [ ] **Step 1: Remove all `is_jumping` / `press_time` remnants**

Run: `grep -rn "is_jumping\|press_time" . --include=*.py`
Expected: no matches. (Old code removed in Tasks 1–3.)

- [ ] **Step 2: Full test run**

Run: `pytest -q`
Expected: all passing.

- [ ] **Step 3: Playtest**

Run: `python main.py`
Expected: player falls, bounces off platforms, steers with `←`/`→`, score climbs, falling off bottom triggers "Game Over", SPACE restarts.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: verify endless jumper gameplay"
```

---

## Self-Review Notes

- **Spec coverage resolved:** score = accumulating scroll (Task 3 ‡6/components); game over = `player.rect.top > SCREEN_HEIGHT` (Task 3); restart via SPACE (Task 3); auto-bounce (Task 1); endless platform generation/prune (Task 2/3); all `is_jumping`/`press_time` removed (Task 4). Spec's deferred items (moving/disappearing platforms, mouse, audio, `.png` assets, packaging) intentionally not implemented.
- **Type consistency:** `check_events(player)` → returns `"restart"` or `None`; `update_screen(screen, player, platforms) -> int`. All names match across tasks. `Platform.rect` and generator function names consistent between Task 2 and Task 3 usages.

**Ready to execute.**
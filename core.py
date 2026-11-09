"""Pure headless engine for Jump Jump.

This module has NO pygame / SDL dependency. It implements the entire game
simulation -- physics, platform generation, collision, scrolling, scoring and
game-over rules -- with plain Python so that any program can import and drive
it without a display.
"""

import random

# --------------------------------------------------------------------------- #
# Tuning constants
# --------------------------------------------------------------------------- #
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 60

GRAVITY = 0.5
MAX_FALL_SPEED = 20       # capped at platform height so we never tunnel through
PLAYER_SPEED = 6
BOUNCE_VELOCITY = -14

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 150

PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_MIN_GAP = 60
PLATFORM_MAX_GAP = 120
HORIZ_REACH = 120            # max horizontal offset from one ledge to the next
START_PLATFORM_TOP = SCREEN_HEIGHT - 100

SHIFT_THRESHOLD = 150        # px from the top where the camera starts scrolling
SUNRISE_AT_SCORE = 2000.0    # by this score the sky reaches full dawn


# --------------------------------------------------------------------------- #
# Entities
# --------------------------------------------------------------------------- #
class Platform:
    """A static landing ledge. Coordinates: (x, y) is its top-left corner."""

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + PLATFORM_HEIGHT

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + PLATFORM_WIDTH

    @property
    def centerx(self):
        return self.x + PLATFORM_WIDTH // 2


class Player:
    """The jumping character. Screen coords; larger y is lower on screen."""

    def __init__(self):
        self.x = PLAYER_START_X - PLAYER_WIDTH // 2
        self.y = float(PLAYER_START_Y - PLAYER_HEIGHT // 2)
        self.vy = 0.0
        self.dir = 0  # -1, 0, +1

    # -- geometry ----------------------------------------------------------- #
    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + PLAYER_HEIGHT

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + PLAYER_WIDTH

    @property
    def centerx(self):
        return self.x + PLAYER_WIDTH // 2

    # -- physics ------------------------------------------------------------ #
    def move_horizontal(self):
        self.x += self.dir * PLAYER_SPEED
        if self.x < 0:
            self.x = 0
        if self.right > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - PLAYER_WIDTH

    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        self.y += self.vy


# --------------------------------------------------------------------------- #
# Collision / help
# --------------------------------------------------------------------------- #
def _overlaps(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x2 < x1 + w1
            and y1 < y2 + h2 and y2 < y1 + h1)


def _bounce(player, platforms):
    """Auto-bounce the player off a ledge if landing from above."""
    if player.vy <= 0:
        return False
    prev_bottom = player.bottom - player.vy
    for plat in platforms:
        if (_overlaps(player.left, player.top, PLAYER_WIDTH, PLAYER_HEIGHT,
                      plat.left, plat.top, PLATFORM_WIDTH, PLATFORM_HEIGHT)
                and prev_bottom <= plat.top):
            player.vy = BOUNCE_VELOCITY
            player.y = plat.top - PLAYER_HEIGHT
            return True
    return False


# --------------------------------------------------------------------------- #
# World generation
# --------------------------------------------------------------------------- #
def _next_y(top, rng=None):
    rng = rng if rng is not None else random
    return top - rng.randint(PLATFORM_MIN_GAP, PLATFORM_MAX_GAP)


def _next_x(prev_centerx, rng=None):
    rng = rng if rng is not None else random
    center = prev_centerx + rng.randint(-HORIZ_REACH, HORIZ_REACH)
    center = max(PLATFORM_WIDTH // 2,
                 min(SCREEN_WIDTH - PLATFORM_WIDTH // 2, center))
    return center - PLATFORM_WIDTH // 2


def generate_initial_platforms(rng=None):
    plats = [Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2,
                      START_PLATFORM_TOP)]
    while plats[-1].top > 0:
        plats.append(Platform(_next_x(plats[-1].centerx, rng), _next_y(plats[-1].top, rng)))
    return plats


def refill_platforms(plats, rng=None):
    if not plats:
        plats.append(Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2,
                              START_PLATFORM_TOP))
    while plats[-1].top > 0:
        plats.append(Platform(_next_x(plats[-1].centerx, rng), _next_y(plats[-1].top, rng)))


def remove_platforms_below(plats, screen_height=SCREEN_HEIGHT):
    for plat in list(plats):
        if plat.top > screen_height:
            plats.remove(plat)


# --------------------------------------------------------------------------- #
# The Game
# --------------------------------------------------------------------------- #
class Game:
    """Headless runnable game. Drive it with `step(action)`."""

    def __init__(self, seed=None):
        self.seed = seed
        self.reset()

    def reset(self):
        # Private RNG avoids resetting the host application's global random state.
        # Recreating it on reset gives the exact same level for a seeded replay.
        self._rng = random.Random(self.seed)
        self.player = Player()
        self.platforms = generate_initial_platforms(self._rng)
        self.score = 0
        self.state = "playing"
        self.frame = 0
        self.direction = 0
        return self.snapshot()

    def progress(self):
        return min(1.0, self.score / SUNRISE_AT_SCORE)

    def step(self, action=None):
        """Advance one frame of simulation given an optional action string.

        Actions: 'left' | 'right' | 'stop' | 'space' | 'q' | None.
        """
        if action == "left":
            self.direction = -1
        elif action == "right":
            self.direction = 1
        elif action == "stop":
            self.direction = 0
        elif action == "space" and self.state == "game_over":
            self.reset()
            return self.snapshot()
        elif action == "q":
            return None

        if self.state != "playing":
            self.frame += 1
            return self.snapshot()

        player = self.player
        player.dir = self.direction
        player.move_horizontal()
        player.apply_gravity()
        _bounce(player, self.platforms)

        scroll = 0
        if player.top < SHIFT_THRESHOLD:
            scroll = SHIFT_THRESHOLD - int(player.top)
            player.y = float(SHIFT_THRESHOLD)
            for plat in self.platforms:
                plat.y += scroll

        refill_platforms(self.platforms, self._rng)
        remove_platforms_below(self.platforms)

        self.score += scroll
        if player.top > SCREEN_HEIGHT:
            self.state = "game_over"

        self.frame += 1
        return self.snapshot()

    def snapshot(self):
        return {
            "frame": self.frame,
            "state": self.state,
            "score": int(self.score),
            "progress": round(self.progress(), 3),
            "player": {"x": int(self.player.x), "y": int(self.player.y),
                       "vy": round(self.player.vy, 2),
                       "dir": self.player.dir},
            "platforms": len(self.platforms),
        }
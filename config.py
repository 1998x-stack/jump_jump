# config.py

# Screen settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Physics
GRAVITY = 0.5
MAX_FALL_SPEED = 20  # cap fall speed at platform height so we never tunnel through

# Player settings
PLAYER_SIZE = (50, 50)
PLAYER_START_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# Player colors/motion
PLAYER_COLOR = (0, 255, 0)
PLAYER_SPEED = 6
BOUNCE_VELOCITY = -14

# Platform settings
PLATFORM_SIZE = (100, 20)
PLATFORM_COLOR = (255, 0, 0)
PLATFORM_MIN_GAP = 60
PLATFORM_MAX_GAP = 120
HORIZ_REACH = 120  # max horizontal offset from one platform to the next (reachable)

# Camera
SHIFT_THRESHOLD = 150   # px from top where the camera starts scrolling
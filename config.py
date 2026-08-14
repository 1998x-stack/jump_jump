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

# Theme: Rising at Golden Hour
SKY_TOP_DUSK = (42, 47, 90)        # deep indigo at the top (start)
SKY_MID_DUSK = (90, 91, 160)       # dusk mid-band
SKY_TOP_DAWN = (252, 170, 138)     # dawn top-tint (high altitude)
SKY_MID_DAWN = (255, 210, 166)     # dawn mid-tint
SKY_HORIZON = (246, 227, 201)      # warm cream horizon (bottom)
PLATFORM_TOP = (255, 246, 228)     # cream ledge top
PLATFORM_BODY = (216, 192, 142)    # ledge body
PLATFORM_EDGE = (196, 168, 116)    # ledge underside
PLAYER_COLOR = (242, 104, 90)      # coral character
PLAYER_CORE = (255, 191, 164)      # lighter core glow
PLAYER_OUTLINE = (148, 62, 66)     # character outline
SCORE_TEXT = (255, 246, 228)       # warm cream text
SHADOW = (30, 28, 55)              # soft drop-shadow
STAR_COLOR = (255, 246, 228)       # drifting dust specks
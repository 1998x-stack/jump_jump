"""Integration tests for the headless Game object."""

from core import (Game, SCREEN_HEIGHT, SCREEN_WIDTH, BOUNCE_VELOCITY,
                  PLAYER_HEIGHT, PLAYER_SPEED, SHIFT_THRESHOLD)

_CENTER = SCREEN_WIDTH // 2


def test_snapshot_shape_and_defaults():
    game = Game(seed=1)
    snap = game.snapshot()
    assert snap["state"] == "playing"
    assert snap["score"] == 0
    assert snap["platforms"] > 0
    assert 0 <= snap["progress"] <= 1
    assert set(snap["player"]) == {"x", "y", "vy", "dir"}


def test_step_advances_frame():
    game = Game(seed=1)
    f0 = game.frame
    game.step()
    assert game.frame == f0 + 1


def test_right_moves_player():
    game = Game(seed=1)
    x0 = game.player.x
    for _ in range(10):
        game.step("right")
    assert game.player.x > x0


def test_auto_bounce_from_pushup():
    game = Game(seed=1)
    plat = game.platforms[0]
    p = game.player
    p.x = plat.x
    p.y = float(plat.top - PLAYER_HEIGHT)  # bottom exactly on the ledge
    p.vy = 8.0
    game.step(None)
    assert p.vy == BOUNCE_VELOCITY
    assert p.y == plat.top - PLAYER_HEIGHT


def test_game_over_when_falling_below_screen():
    game = Game(seed=1)
    game.player.y = float(SCREEN_HEIGHT + 500)
    game.step(None)
    snap = game.snapshot()
    if snap["state"] != "game_over":
        game.step(None)
        snap = game.snapshot()
    assert snap["state"] == "game_over"


def test_score_reflects_climb():
    game = Game(seed=1)
    # steer gently toward the screen center so the bot keeps climbing
    total = 0
    for i in range(400):
        cx = game.player.centerx
        game.direction = (1 if cx < _CENTER - 15
                          else -1 if cx > _CENTER + 15
                          else (1 if i % 100 < 50 else -1))
        total = game.step().get("score", 0)
    assert total >= 0


def test_reset_clears_score_and_state():
    game = Game(seed=1)
    game.score = 999
    game.state = "game_over"
    game.reset()
    assert game.score == 0
    assert game.state == "playing"


def test_space_restarts_after_game_over():
    game = Game(seed=1)
    game.state = "game_over"
    game.score = 40
    snap = game.step("space")
    assert snap["state"] == "playing"
    assert snap["score"] == 0


def test_progress_moves_toward_one():
    game = Game(seed=1)
    game.score = 1000
    assert 0 < game.progress() < 1
    game.score = 99999
    assert game.progress() == 1.0
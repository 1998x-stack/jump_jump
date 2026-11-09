"""Property tests for isolated seeded game simulations."""
import random
from core import Game, generate_initial_platforms

def platforms(game):
    return [(p.x, p.y) for p in game.platforms]

def test_seed_does_not_modify_global_rng():
    random.seed(2026)
    expected = [random.random() for _ in range(5)]
    random.seed(2026)
    game = Game(seed=7)
    for _ in range(500):
        game.step("right")
    assert [random.random() for _ in range(5)] == expected

def test_seeded_games_do_not_interfere_when_interleaved():
    first = Game(seed=8)
    second = Game(seed=42)
    baseline = Game(seed=8)
    for _ in range(700):
        first.step("left")
        second.step("right")
        baseline.step("left")
    assert first.snapshot() == baseline.snapshot()
    assert platforms(first) == platforms(baseline)

def test_reset_restores_initial_platform_layout():
    game = Game(seed=19)
    initial = platforms(game)
    for _ in range(200):
        game.step("left")
    game.reset()
    assert platforms(game) == initial
    assert game.frame == 0 and game.score == 0

def test_explicit_rng_is_reproducible_for_level_generation():
    left = generate_initial_platforms(random.Random(99))
    right = generate_initial_platforms(random.Random(99))
    assert [(p.x, p.y) for p in left] == [(p.x, p.y) for p in right]

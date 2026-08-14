"""CLI tests for the headless runner (no display needed)."""

import json
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(lines, *args):
    return subprocess.run(
        [sys.executable, "main.py", *args],
        input="\n".join(lines),
        capture_output=True, text=True, cwd=_ROOT, timeout=60)


def test_headless_emits_one_json_line_per_frame():
    proc = _run(["right", "right", "right"], "--headless", "--seed", "1")
    assert proc.returncode == 0, proc.stderr
    lines = [json.loads(l) for l in proc.stdout.strip().splitlines()]
    assert len(lines) == 3
    frames = [l["frame"] for l in lines]
    assert frames == [1, 2, 3]
    assert all(l["state"] == "playing" for l in lines)


def test_headless_right_steering_moves_player():
    proc = _run(["right", "right", "right", "right"], "--headless", "--seed", "1")
    lines = [json.loads(l) for l in proc.stdout.strip().splitlines()]
    assert lines[-1]["player"]["x"] > lines[0]["player"]["x"]


def test_headless_quit_stops_cleanly():
    proc = _run(["q"], "--headless", "--seed", "1")
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_headless_is_full_json_snapshot():
    proc = _run(["left"], "--headless", "--seed", "2")
    snap = json.loads(proc.stdout.strip().splitlines()[-1])
    assert {"frame", "state", "score", "progress", "player", "platforms"} == \
        set(snap)
    assert set(snap["player"]) == {"x", "y", "vy", "dir"}
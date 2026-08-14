# Jump Jump — Golden Hour

An endless "jump jump" (Doodle-Jump-style) climber. Bounce up a tower of
ledges through a dusk sky that tilts toward dawn as you climb. Steer left and
right; landing on a ledge auto-bounces you upward.

Architected **headless-first**: the whole simulation lives in a pure-Python
engine (`core.py`, no pygame), so it can be imported and driven by other
programs without any display. Rendering is a thin pygame layer (`view.py`).

## Layout

| File | Responsibility |
|------|----------------|
| `core.py` | Pure headless engine: physics, platforms, scoring, game-over, `Game` API (no pygame/SDL) |
| `view.py` | pygame renderer: Golden Hour theme, sky, dust, ledges, character, score |
| `main.py` | CLI: interactive windowed game **or** `--headless` stdin/stdout runner |
| `tests/` | `test_core`, `test_game`, `test_view`, `test_headless` |

## Run

Interactive windowed game:

```bash
pip install -r requirements.txt
python main.py
```

Controls: `←`/`A` and `→`/`D` to steer; `SPACE` to restart after game over.

Test suite:

```bash
python -m pytest -q
```

## Headless mode

Drive the game from another program over stdin, reading one JSON state line
per frame on stdout. **No window is opened and pygame isn't even loaded.**

```bash
python main.py --headless --seed 1
```

Pipe one command per line:

| command   | effect                                |
|-----------|---------------------------------------|
| `left`    | steer left                            |
| `right`   | steer right                           |
| `stop`    | stop steering                         |
| `space`   | restart (in game-over state)          |
| *(blank)* | keep current direction (advance frame)|
| `q`       | exit                                  |

Each line produces one frame, so the driver controls pacing. Example:

```bash
printf 'right\nright\nspace\nq\n' | python main.py --headless
```

Output is one JSON object per frame:

```json
{"frame": 1, "state": "playing", "score": 0, "progress": 0.0,
 "player": {"x": 240, "y": 625, "vy": 0.5, "dir": 1},
 "platforms": 10}
```

## Scripted batch mode

Run a fixed, rerunnable `JSON` action recipe (a deterministic replay):

```bash
python main.py --script replay.json    # or: --script -  (JSON from stdin)
```

```json
{
  "seed": 123,
  "actions": [
    { "action": "right", "frames": 20 },
    { "action": "space", "frames": 1 },
    { "frames": 5 }          // action omitted → keep current direction
  ]
}
```

For each entry the runner repeats `action` for `frames` frames, printing one
JSON state line per frame, then a final summary line:

```json
{"done": true, "frames": 8, "final_state": "playing", "score": 0,
 "progress": 0.0, "player": {"x": 203, "y": 643}}
```

Same recipe + seed always produces identical output, so scripts are
deterministic and rerunnable.

### Using the engine directly (no CLI)

```python
from core import Game

game = Game(seed=7)          # reproducible world
for _ in range(120):
    snap = game.step("right")    # steer right one frame
print(snap["state"], snap["score"])
```
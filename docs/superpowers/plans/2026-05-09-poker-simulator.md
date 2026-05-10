# Poker Hand Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Shiny for Python (Core mode) poker hand simulator that runs 5,000 Monte Carlo Texas Hold'em deals and displays win rate + top hand breakdowns with inline bar charts.

**Architecture:** `simulation.py` handles all poker math with no Shiny dependency; `ui.py` defines a two-column layout using shinyswatch darkly theme; `server.py` connects button clicks to the simulation and renders results as HTML; `app.py` wires everything together.

**Tech Stack:** Python 3.9+, shiny, shinyswatch, pytest

---

### Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`
- Create: `app.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
shiny
shinyswatch
pytest
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install without error.

- [ ] **Step 3: Create minimal app.py**

```python
from shiny import App, ui

app_ui = ui.page_fluid(ui.h2("Poker Hand Simulator"))

def server(input, output, session):
    pass

app = App(app_ui, server)
```

- [ ] **Step 4: Verify the app starts**

Run: `shiny run app.py`
Expected: Server starts at http://127.0.0.1:8000. Browser shows a heading "Poker Hand Simulator". Stop with Ctrl+C.

- [ ] **Step 5: Create the tests directory**

Run: `mkdir tests && touch tests/__init__.py`

- [ ] **Step 6: Initialize git and commit**

```bash
git init
git add requirements.txt app.py tests/__init__.py
git commit -m "feat: project scaffold"
```

---

### Task 2: Card parsing (`simulation.py`)

**Files:**
- Create: `simulation.py`
- Create: `tests/test_simulation.py`

- [ ] **Step 1: Write failing tests for parse_cards**

Create `tests/test_simulation.py`:

```python
from simulation import parse_cards


class TestParseCards:
    def test_valid_input(self):
        cards, err = parse_cards("AH KS")
        assert cards == [('A', 'H'), ('K', 'S')]
        assert err is None

    def test_valid_lowercase(self):
        cards, err = parse_cards("ah ks")
        assert cards == [('A', 'H'), ('K', 'S')]
        assert err is None

    def test_empty_string(self):
        cards, err = parse_cards("")
        assert cards is None
        assert err == "Please enter your two hole cards"

    def test_whitespace_only(self):
        cards, err = parse_cards("   ")
        assert cards is None
        assert err == "Please enter your two hole cards"

    def test_one_card_only(self):
        cards, err = parse_cards("AH")
        assert cards is None
        assert err == "Please enter exactly two cards"

    def test_three_cards(self):
        cards, err = parse_cards("AH KS QD")
        assert cards is None
        assert err == "Please enter exactly two cards"

    def test_invalid_rank(self):
        cards, err = parse_cards("XH KS")
        assert cards is None
        assert "Invalid card: XH" in err

    def test_invalid_suit(self):
        cards, err = parse_cards("AX KS")
        assert cards is None
        assert "Invalid card: AX" in err

    def test_duplicate_card(self):
        cards, err = parse_cards("AH AH")
        assert cards is None
        assert "Duplicate card: AH" in err

    def test_ten_shorthand(self):
        cards, err = parse_cards("TH 9S")
        assert cards == [('T', 'H'), ('9', 'S')]
        assert err is None
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_simulation.py::TestParseCards -v`
Expected: `ModuleNotFoundError: No module named 'simulation'`

- [ ] **Step 3: Create simulation.py with parse_cards**

```python
import random
from itertools import combinations

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['H', 'D', 'C', 'S']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}
HAND_NAMES = [
    "High Card", "Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind",
    "Straight Flush", "Royal Flush",
]


def make_deck():
    return [(r, s) for r in RANKS for s in SUITS]


def parse_cards(text):
    """Parse 'AH KS' into [('A','H'),('K','S')], or return (None, error_str)."""
    if not text or not text.strip():
        return None, "Please enter your two hole cards"
    tokens = text.strip().upper().split()
    if len(tokens) != 2:
        return None, "Please enter exactly two cards"
    cards = []
    for token in tokens:
        if len(token) != 2 or token[0] not in RANK_VALUES or token[1] not in SUITS:
            return None, f"Invalid card: {token}. Use ranks 2–9 T J Q K A and suits H D C S"
        cards.append((token[0], token[1]))
    if cards[0] == cards[1]:
        return None, f"Duplicate card: {tokens[0]}"
    return cards, None
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_simulation.py::TestParseCards -v`
Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add simulation.py tests/test_simulation.py
git commit -m "feat: add card parsing"
```

---

### Task 3: Hand evaluator (`simulation.py`)

**Files:**
- Modify: `simulation.py` — add `_score_5`, `best_hand_score`, `eval_hand`
- Modify: `tests/test_simulation.py` — add `TestEvalHand`

- [ ] **Step 1: Write failing tests for eval_hand**

Add this class to `tests/test_simulation.py`:

```python
from simulation import eval_hand


class TestEvalHand:
    def test_royal_flush(self):
        cards = [('A','H'),('K','H'),('Q','H'),('J','H'),('T','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Royal Flush"

    def test_straight_flush(self):
        cards = [('9','H'),('8','H'),('7','H'),('6','H'),('5','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Straight Flush"

    def test_four_of_a_kind(self):
        cards = [('A','H'),('A','S'),('A','D'),('A','C'),('K','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Four of a Kind"

    def test_full_house(self):
        cards = [('A','H'),('A','S'),('A','D'),('K','C'),('K','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Full House"

    def test_flush(self):
        cards = [('A','H'),('K','H'),('Q','H'),('J','H'),('9','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Flush"

    def test_straight(self):
        cards = [('A','H'),('K','S'),('Q','D'),('J','C'),('T','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Straight"

    def test_wheel_straight(self):
        # A-2-3-4-5: ace plays low
        cards = [('A','H'),('2','S'),('3','D'),('4','C'),('5','H'),('K','S'),('Q','D')]
        assert eval_hand(cards) == "Straight"

    def test_three_of_a_kind(self):
        cards = [('A','H'),('A','S'),('A','D'),('K','C'),('Q','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Three of a Kind"

    def test_two_pair(self):
        cards = [('A','H'),('A','S'),('K','D'),('K','C'),('Q','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Two Pair"

    def test_pair(self):
        cards = [('A','H'),('A','S'),('K','D'),('Q','C'),('J','H'),('2','S'),('3','D')]
        assert eval_hand(cards) == "Pair"

    def test_high_card(self):
        cards = [('A','H'),('K','S'),('Q','D'),('J','C'),('9','H'),('7','S'),('2','D')]
        assert eval_hand(cards) == "High Card"

    def test_picks_best_hand_from_seven(self):
        # 5 hearts available → should find the flush
        cards = [('2','H'),('5','H'),('7','H'),('J','H'),('K','H'),('A','S'),('3','D')]
        assert eval_hand(cards) == "Flush"
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_simulation.py::TestEvalHand -v`
Expected: `ImportError: cannot import name 'eval_hand'`

- [ ] **Step 3: Add hand evaluator to simulation.py**

Add these three functions after `parse_cards` in `simulation.py`:

```python
def _score_5(cards):
    """Score a 5-card hand. Returns a comparable tuple; higher tuple = stronger hand."""
    ranks = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    is_flush = len(set(suits)) == 1
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    counts = sorted(rank_counts.values(), reverse=True)
    # Detect straight, including A-2-3-4-5 wheel
    is_straight = False
    straight_ranks = ranks
    if len(set(ranks)) == 5:
        if ranks[0] - ranks[4] == 4:
            is_straight = True
        elif set(ranks) == {12, 3, 2, 1, 0}:  # A-2-3-4-5
            is_straight = True
            straight_ranks = [3, 2, 1, 0, -1]  # ace plays below 2
    if is_straight and is_flush:
        if straight_ranks[0] == 12:
            return (9,) + tuple(straight_ranks)  # Royal Flush
        return (8,) + tuple(straight_ranks)      # Straight Flush
    if counts[0] == 4:
        return (7,) + tuple(ranks)               # Four of a Kind
    if counts[:2] == [3, 2]:
        return (6,) + tuple(ranks)               # Full House
    if is_flush:
        return (5,) + tuple(ranks)               # Flush
    if is_straight:
        return (4,) + tuple(straight_ranks)      # Straight
    if counts[0] == 3:
        return (3,) + tuple(ranks)               # Three of a Kind
    if counts[:2] == [2, 2]:
        return (2,) + tuple(ranks)               # Two Pair
    if counts[0] == 2:
        return (1,) + tuple(ranks)               # Pair
    return (0,) + tuple(ranks)                   # High Card


def best_hand_score(cards):
    """Return the best score tuple from 5–7 cards (checks all C(n,5) combinations)."""
    best = None
    for combo in combinations(cards, 5):
        score = _score_5(combo)
        if best is None or score > best:
            best = score
    return best


def eval_hand(cards):
    """Return the hand name string for the best 5-card hand from 5–7 cards."""
    return HAND_NAMES[best_hand_score(cards)[0]]
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_simulation.py::TestEvalHand -v`
Expected: All 12 tests PASS.

- [ ] **Step 5: Run the full suite to confirm nothing broke**

Run: `pytest tests/ -v`
Expected: All 22 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add simulation.py tests/test_simulation.py
git commit -m "feat: add hand evaluator"
```

---

### Task 4: Simulation loop (`simulation.py`)

**Files:**
- Modify: `simulation.py` — add `run_simulation`
- Modify: `tests/test_simulation.py` — add `TestRunSimulation`

- [ ] **Step 1: Write failing tests for run_simulation**

Add this class to `tests/test_simulation.py`:

```python
from simulation import run_simulation, HAND_NAMES


class TestRunSimulation:
    def test_returns_required_keys(self):
        result = run_simulation([('A','H'),('K','S')], n_opponents=2, n_sims=100)
        assert "win_pct" in result
        assert "won_with" in result
        assert "lost_to" in result

    def test_win_pct_in_valid_range(self):
        result = run_simulation([('A','H'),('K','S')], n_opponents=2, n_sims=200)
        assert 0 <= result["win_pct"] <= 100

    def test_pocket_aces_favored_heads_up(self):
        result = run_simulation([('A','H'),('A','S')], n_opponents=1, n_sims=1000)
        assert result["win_pct"] > 50

    def test_won_with_keys_are_valid_hand_names(self):
        result = run_simulation([('A','H'),('A','S')], n_opponents=2, n_sims=200)
        for name in result["won_with"]:
            assert name in HAND_NAMES

    def test_lost_to_keys_are_valid_hand_names(self):
        result = run_simulation([('2','H'),('7','S')], n_opponents=2, n_sims=200)
        for name in result["lost_to"]:
            assert name in HAND_NAMES

    def test_won_with_sorted_descending(self):
        result = run_simulation([('A','H'),('A','S')], n_opponents=1, n_sims=500)
        counts = list(result["won_with"].values())
        assert counts == sorted(counts, reverse=True)
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_simulation.py::TestRunSimulation -v`
Expected: `ImportError: cannot import name 'run_simulation'`

- [ ] **Step 3: Add run_simulation to simulation.py**

Add after `eval_hand` in `simulation.py`:

```python
def run_simulation(hole_cards, n_opponents, n_sims=5000):
    """
    Monte Carlo simulation of n_sims Texas Hold'em hands.
    Returns {"win_pct": float, "won_with": {hand: count}, "lost_to": {hand: count}}.
    Ties (split pots) are not counted as wins and not recorded in lost_to.
    """
    deck = [c for c in make_deck() if c not in hole_cards]
    wins = 0
    won_with = {}
    lost_to = {}

    for _ in range(n_sims):
        shuffled = deck.copy()
        random.shuffle(shuffled)
        community = shuffled[:5]
        opp_pool = shuffled[5:5 + n_opponents * 2]

        player_score = best_hand_score(hole_cards + community)
        player_hand = HAND_NAMES[player_score[0]]

        opp_scores = [
            best_hand_score(opp_pool[i * 2:(i + 1) * 2] + community)
            for i in range(n_opponents)
        ]

        if all(player_score > s for s in opp_scores):
            wins += 1
            won_with[player_hand] = won_with.get(player_hand, 0) + 1
        else:
            beating = [s for s in opp_scores if s > player_score]
            if beating:
                best_opp = HAND_NAMES[max(beating)[0]]
                lost_to[best_opp] = lost_to.get(best_opp, 0) + 1

    return {
        "win_pct": round(wins / n_sims * 100, 1),
        "won_with": dict(sorted(won_with.items(), key=lambda x: x[1], reverse=True)),
        "lost_to": dict(sorted(lost_to.items(), key=lambda x: x[1], reverse=True)),
    }
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_simulation.py::TestRunSimulation -v`
Expected: All 6 tests PASS. (The pocket aces test runs 1,000 simulations — allow a few seconds.)

- [ ] **Step 5: Run full suite**

Run: `pytest tests/ -v`
Expected: All 28 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add simulation.py tests/test_simulation.py
git commit -m "feat: add Monte Carlo simulation loop"
```

---

### Task 5: UI layout (`ui.py`)

**Files:**
- Create: `ui.py`
- Modify: `app.py` — import `app_ui` from `ui.py`

- [ ] **Step 1: Create ui.py**

```python
from shiny import ui
import shinyswatch

app_ui = ui.page_fluid(
    shinyswatch.theme.darkly(),
    ui.div(
        ui.h2("Poker Hand Simulator"),
        style="margin: 16px 0 24px;",
    ),
    ui.row(
        ui.column(
            4,
            ui.card(
                ui.card_header("Setup"),
                ui.input_numeric(
                    "n_opponents", "Number of opponents",
                    value=2, min=1, max=5, step=1,
                ),
                ui.input_text(
                    "hole_cards", "Your hole cards",
                    placeholder="AH KS",
                ),
                ui.p(
                    ui.em("Ranks: 2–9 T J Q K A  |  Suits: H D C S"),
                    style="color: #aaa; font-size: 0.85em; margin-top: -8px;",
                ),
                ui.input_action_button(
                    "run_btn", "Run Simulation",
                    class_="btn-success w-100 mt-2",
                ),
                ui.output_ui("error_msg"),
            ),
        ),
        ui.column(
            8,
            ui.output_ui("results_panel"),
        ),
    ),
)
```

- [ ] **Step 2: Update app.py to import from ui.py**

```python
from shiny import App
from ui import app_ui


def server(input, output, session):
    pass


app = App(app_ui, server)
```

- [ ] **Step 3: Verify the UI renders correctly**

Run: `shiny run app.py --reload`
Expected: Dark-themed page. Left column shows a card with "Setup" header, numeric input, text input, helper text, and green button. Right column is empty. Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add ui.py app.py
git commit -m "feat: add two-column UI with shinyswatch dark theme"
```

---

### Task 6: Server logic (`server.py`)

**Files:**
- Create: `server.py`
- Modify: `app.py` — import `server` from `server.py`

- [ ] **Step 1: Create server.py**

```python
from shiny import render, reactive, ui
from simulation import parse_cards, run_simulation


def server(input, output, session):
    _result = reactive.value(None)
    _error = reactive.value("")

    @reactive.effect
    @reactive.event(input.run_btn)
    def _on_run():
        cards, err = parse_cards(input.hole_cards())
        if err:
            _error.set(err)
            _result.set(None)
            return
        _error.set("")
        data = run_simulation(cards, input.n_opponents())
        _result.set({
            "data": data,
            "label": (
                f"{input.hole_cards().strip().upper()} vs "
                f"{input.n_opponents()} opponent"
                f"{'s' if input.n_opponents() > 1 else ''}"
            ),
        })

    @output
    @render.ui
    def error_msg():
        msg = _error.get()
        if msg:
            return ui.p(msg, style="color: #e74c3c; margin-top: 8px;")
        return ui.div()

    @output
    @render.ui
    def results_panel():
        payload = _result.get()
        if payload is None:
            return ui.div()

        data = payload["data"]
        label = payload["label"]
        win_pct = data["win_pct"]
        won_with = data["won_with"]
        lost_to = data["lost_to"]
        banner_color = "#27ae60" if win_pct >= 50 else "#e74c3c"

        def bar_rows(hand_dict, color):
            total = sum(hand_dict.values())
            rows = []
            for name, count in list(hand_dict.items())[:5]:
                pct = round(count / total * 100, 1) if total > 0 else 0
                rows.append(ui.div(
                    ui.div(
                        ui.span(name),
                        ui.span(f"{pct}%", style=f"color: {color};"),
                        style="display:flex; justify-content:space-between; margin-bottom:3px;",
                    ),
                    ui.div(
                        ui.div(style=(
                            f"background:{color}; width:{pct}%;"
                            "height:6px; border-radius:3px;"
                        )),
                        style="background:#444; border-radius:3px; height:6px; margin-bottom:10px;",
                    ),
                ))
            return rows

        return ui.div(
            ui.div(
                ui.h2(f"{win_pct}% Win Rate", style="margin:0; color:white;"),
                ui.p(
                    f"{label} — 5,000 hands",
                    style="margin:4px 0 0; color:rgba(255,255,255,0.8); font-size:0.9em;",
                ),
                style=(
                    f"background:{banner_color}; border-radius:8px;"
                    "padding:20px 24px; margin-bottom:20px;"
                ),
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(
                            ui.span("Won With", style="color:#2ecc71; font-weight:bold;")
                        ),
                        *bar_rows(won_with, "#2ecc71"),
                    ),
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(
                            ui.span("Lost To", style="color:#e74c3c; font-weight:bold;")
                        ),
                        *bar_rows(lost_to, "#e74c3c"),
                    ),
                ),
            ),
        )
```

- [ ] **Step 2: Update app.py to import from server.py**

```python
from shiny import App
from ui import app_ui
from server import server

app = App(app_ui, server)
```

- [ ] **Step 3: Smoke test the full app**

Run: `shiny run app.py --reload`

Test all four paths:
1. Enter `AH KS`, 2 opponents → "Run Simulation" → win % banner appears with green/red won/lost panels
2. Leave cards blank → click run → red error "Please enter your two hole cards"
3. Enter `XH KS` → click run → red error mentioning "Invalid card: XH"
4. Enter `AH AH` → click run → red error "Duplicate card: AH"
5. Fix the invalid input from step 3 → click run → error clears, results appear

Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add server.py app.py
git commit -m "feat: add reactive server with results rendering"
```

---

### Task 7: Final checks and Posit Connect prep

**Files:**
- Verify: `app.py`, `requirements.txt`

- [ ] **Step 1: Confirm app.py is clean**

`app.py` must contain exactly this — nothing more:

```python
from shiny import App
from ui import app_ui
from server import server

app = App(app_ui, server)
```

- [ ] **Step 2: Confirm requirements.txt**

For Posit Connect deployment, `pytest` is a dev-only tool. The production `requirements.txt` should be:

```
shiny
shinyswatch
```

Keep `pytest` for local development — you can install it separately with `pip install pytest`.

- [ ] **Step 3: Run the full test suite one final time**

Run: `pytest tests/ -v`
Expected: All 28 tests PASS.

- [ ] **Step 4: Full manual end-to-end test**

Run: `shiny run app.py`

Golden path checklist:
- [ ] `AH KS` vs 3 opponents → results show, banner is green (AK is a strong hand)
- [ ] `2H 7S` vs 5 opponents → results show, banner is red (2-7 offsuit is the worst hand)
- [ ] Resize browser → columns reflow without breaking layout
- [ ] Change opponents count → old results stay visible until "Run" clicked again
- [ ] Run twice with different inputs → results update correctly each time

- [ ] **Step 5: Final commit**

```bash
git add requirements.txt
git commit -m "feat: complete poker hand simulator, ready for Posit Connect"
```

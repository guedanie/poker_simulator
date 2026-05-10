# Poker Hand Simulator — Design Spec
**Date:** 2026-05-09  
**Framework:** Shiny for Python (Core mode)  
**Deployment target:** Posit Connect

---

## Overview

A Shiny for Python app where the user enters their two hole cards and number of opponents, clicks "Run Simulation", and sees what percentage of 5,000 simulated Texas Hold'em hands they would win — along with which hand types they won with and lost to most often. No bluffs, bets, or folding — pure hand-strength simulation.

---

## Architecture

Four files, each with one clear responsibility:

| File | Responsibility |
|---|---|
| `app.py` | Entry point — wires `app_ui` and `server` into `App()`, nothing else |
| `ui.py` | All layout and input widgets — returns `app_ui` |
| `server.py` | Reactive logic — listens to inputs, calls simulation, renders outputs |
| `simulation.py` | Pure Python poker math — no Shiny imports, fully testable in isolation |
| `requirements.txt` | Declares `shiny`, `shinyswatch`, `pandas` for Posit Connect deployment |

---

## Simulation Engine (`simulation.py`)

### Card Representation
Each card is a tuple `(rank, suit)`. Valid ranks: `2–9, T, J, Q, K, A`. Valid suits: `H, D, C, S`. Example: `('A', 'H')` = Ace of Hearts. The full deck is all 52 `(rank, suit)` combinations.

### Card Parsing
`parse_cards(text: str) -> list[tuple]`  
Converts shorthand like `"AH KS"` into `[('A', 'H'), ('K', 'S')]`. Returns a clear error string on invalid input.

### Hand Evaluator
`eval_hand(cards: list[tuple]) -> str`  
Takes exactly 7 cards (2 hole + 5 community), returns the best 5-card hand type as a string. Hand rankings (low to high):

1. High Card
2. Pair
3. Two Pair
4. Three of a Kind
5. Straight
6. Flush
7. Full House
8. Four of a Kind
9. Straight Flush
10. Royal Flush

### Simulation Loop
`run_simulation(hole_cards, n_opponents, n_sims=5000) -> dict`

For each of 5,000 iterations:
1. Remove the player's 2 hole cards from the deck
2. Shuffle the remaining 50 cards
3. Deal 5 community cards
4. Deal 2 hole cards to each opponent
5. Evaluate all hands (player + each opponent, each using their 2 hole cards + 5 community cards)
6. If player's hand beats every opponent's hand → win; record player's winning hand type
7. If player loses → record the best opponent hand type that beat the player

**Returns:**
```python
{
    "win_pct": 63.4,
    "won_with": {"Pair": 1400, "High Card": 1100, ...},  # hand → count
    "lost_to":  {"Pair": 740, "Two Pair": 540, ...}       # hand → count
}
```

---

## UI (`ui.py`)

**Theme:** `shinyswatch.theme.darkly()` — dark background, green/white accents.

**Layout:** Two-column `page_fluid` layout.

### Left Column — Controls
- Numeric input: "Number of opponents" (min 1, max 5, default 2)
- Text input: "Your hole cards" — placeholder `AH KS`
- Helper text: `Ranks: 2–9 T J Q K A  |  Suits: H D C S`
- "Run Simulation" action button (full-width, green)
- Error message output (red, shown only on invalid input)

### Right Column — Results
Hidden until the simulation runs. Contains:

1. **Win rate banner** — large colored box:  
   `63.4% Win Rate`  
   subtitle: `AH KS vs 3 opponents — 5,000 hands`

2. **Two side-by-side panels:**
   - **Won With** — top 5 hand types, ranked by frequency, with inline green progress bar + percentage
   - **Lost To** — top 5 hand types, ranked by frequency, with inline red progress bar + percentage

Inline bars are rendered as HTML via `render.ui` — a colored `<div>` sized by percentage width. No charting library needed.

---

## Data Flow

1. User enters hole cards (e.g., `AH KS`), sets opponents (e.g., 3), clicks "Run Simulation"
2. `server.py` fires on button click via `reactive.event`
3. Calls `simulation.parse_cards()` — validates input
4. On valid input: calls `simulation.run_simulation(hole_cards, n_opponents, n_sims=5000)`
5. Results rendered into win % banner + two HTML panels

---

## Error Handling

Errors are shown inline below the card input field. Results panel stays hidden when an error is present.

| Condition | Message |
|---|---|
| Empty input | "Please enter your two hole cards" |
| Invalid card (e.g. `AX`) | "Invalid card: AX. Use ranks 2–9 T J Q K A and suits H D C S" |
| Duplicate card (e.g. `AH AH`) | "Duplicate card: AH" |
| Only one card entered | "Please enter exactly two cards" |

No other input validation — player count slider is bounded by the UI (1–5), and no other impossible states can occur.

---

## Dependencies

```
shiny
shinyswatch
```

No poker-specific packages — hand evaluation is implemented from scratch in `simulation.py` using standard Python. Hand frequency data is plain Python dicts — no data library needed.

---

## Out of Scope

- Bluffing, betting, or fold simulation
- More than 5 opponents
- Saving or replaying simulation results
- Hand history or session tracking

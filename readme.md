# Poker Hand Simulator

A Shiny for Python app that simulates Texas Hold'em hand strength using Monte Carlo methods. Enter your two hole cards and the number of opponents, and the app runs 5,000 simulated hands to estimate how often your hand wins — and what you win and lose to most.

## What It Does

- Select 1–5 opponents (2–6 players total)
- Enter your two hole cards using shorthand notation (e.g. `AH KS` for Ace of Hearts, King of Spades)
- Click **Run Simulation** to run 5,000 Monte Carlo deals
- See your **win rate** as a colored banner (green ≥ 50%, red otherwise)
- See the **top hand types you won with** and **lost to**, ranked by frequency with inline bar charts

No bluffing, betting, or folding — pure hand-strength simulation.

## Card Shorthand

| Symbol | Meaning |
|--------|---------|
| `2`–`9` | Number cards |
| `T` | Ten |
| `J` | Jack |
| `Q` | Queen |
| `K` | King |
| `A` | Ace |
| `H` | Hearts |
| `D` | Diamonds |
| `C` | Clubs |
| `S` | Spades |

Examples: `AH KS` (Ace of Hearts, King of Spades), `TH 9H` (Ten and Nine of Hearts)

## Running Locally

```bash
pip install -r requirements.txt
shiny run app.py --reload
```

App runs at http://127.0.0.1:8000

## Project Structure

```
app.py          # Entry point — wires UI and server
ui.py           # Layout and inputs (shinyswatch dark theme)
server.py       # Reactive logic and results rendering
simulation.py   # Poker math — card parsing, hand evaluation, Monte Carlo loop
tests/          # 31 tests covering parsing, hand evaluation, and simulation
requirements.txt
```

## Deploying to Posit Connect

The app is self-contained with no database or external dependencies. Deploy via the Posit Connect UI or `rsconnect-python`:

```bash
pip install rsconnect-python
rsconnect deploy shiny . --server <your-connect-url> --api-key <your-api-key>
```

## Tech Stack

- [Shiny for Python](https://shiny.posit.co/py/) (Core mode)
- [shinyswatch](https://github.com/posit-dev/py-shinyswatch) — darkly theme
- pytest — 31 tests, TDD throughout

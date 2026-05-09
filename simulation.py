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


def _score_5(cards):
    """Score a 5-card hand. Returns a comparable tuple; higher tuple = stronger hand."""
    ranks = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    is_flush = len(set(suits)) == 1
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    # Sort groups: primary key = count desc, secondary key = rank desc
    # This puts the group (pair/trips/quads) before kickers in the score tuple
    groups = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    ordered_ranks = [r for r, c in groups for _ in range(c)]
    counts = [c for _, c in groups]
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
        return (7,) + tuple(ordered_ranks)       # Four of a Kind
    if counts[:2] == [3, 2]:
        return (6,) + tuple(ordered_ranks)       # Full House
    if is_flush:
        return (5,) + tuple(ranks)               # Flush (no groups, use plain ranks)
    if is_straight:
        return (4,) + tuple(straight_ranks)      # Straight
    if counts[0] == 3:
        return (3,) + tuple(ordered_ranks)       # Three of a Kind
    if counts[:2] == [2, 2]:
        return (2,) + tuple(ordered_ranks)       # Two Pair
    if counts[0] == 2:
        return (1,) + tuple(ordered_ranks)       # Pair
    return (0,) + tuple(ranks)                   # High Card (no groups, use plain ranks)


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

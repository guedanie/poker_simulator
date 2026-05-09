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

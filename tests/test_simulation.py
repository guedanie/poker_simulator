from simulation import parse_cards, eval_hand, run_simulation, HAND_NAMES, best_hand_score


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

    def test_pair_rank_beats_high_kickers(self):
        # Pair of 3s beats pair of 2s even when 2s have AKQ kickers
        threes = best_hand_score([('3','H'),('3','S'),('K','D'),('Q','C'),('J','H'),('2','S'),('4','D')])
        twos   = best_hand_score([('2','H'),('2','S'),('A','D'),('K','C'),('Q','H'),('3','D'),('4','S')])
        assert threes > twos

    def test_full_house_trips_rank_is_primary(self):
        # Threes full of kings beats twos full of aces
        fh_333kk = best_hand_score([('3','H'),('3','S'),('3','D'),('K','C'),('K','H'),('2','S'),('4','D')])
        fh_222aa = best_hand_score([('2','H'),('2','S'),('2','D'),('A','C'),('A','H'),('3','D'),('4','S')])
        assert fh_333kk > fh_222aa

    def test_four_of_a_kind_rank_is_primary(self):
        # Quad 3s beats quad 2s even with ace kicker
        quads_3 = best_hand_score([('3','H'),('3','S'),('3','D'),('3','C'),('A','H'),('K','S'),('2','D')])
        quads_2 = best_hand_score([('2','H'),('2','S'),('2','D'),('2','C'),('A','H'),('K','S'),('3','D')])
        assert quads_3 > quads_2


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

from simulation import parse_cards, eval_hand


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

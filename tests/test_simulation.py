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

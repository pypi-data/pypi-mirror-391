import pytest
from Poker65.card import Card
from Poker65.hands import *

def make_cardlist(card_string : str) -> list[Card]:
    card_strings : list[str] = card_string.split(' ')
    return [Card(rank=Card.rank2int(s[0]), suit=Card.suit2int(s[1])) for s in card_strings]

def test_get_best_hand():
    testcases : list[tuple[str, Hand]] = [
        ('2D 6H 8S KH 5H 3D TC', HighCard(cards=make_cardlist('KH TC 8S 6H 5H'))),
        ('3C 5C 9C 6C 7D 8C 2S', Flush(suit='C', ranks=['3', '5', '9', '6', '8'])),
        ('QC QD KD TS 7C 2C 4C', OnePair(pair_rank='Q', pair_suits=('C', 'D'), kickers=[Card('D', 'K'), Card('S', 'T'), Card('C', '7')])),
        ('JC QH 9S 6S 4H 3S KC', HighCard(cards=make_cardlist('KC QH JC 9S 6S'))),
        ('TH JD AH 9D JS AD 7H', TwoPair(pair1_rank='A', pair1_suits=('H', 'D'), pair2_rank='J', pair2_suits=('D', 'S'), kicker=Card('H', 'T'))),
        ('6S 5D 4H 5C KC 2D 3D', Straight(high='6', suits=['S', 'D', 'H', 'D', 'D'])),
    ]
    for testcase in testcases:
        cardlist, hand = testcase
        assert hand == get_best_hand(make_cardlist(cardlist))

if __name__ == "__main__": 
    pytest.main()

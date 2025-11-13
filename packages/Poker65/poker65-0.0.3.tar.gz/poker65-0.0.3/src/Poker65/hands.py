'''
Author: Daniel Li (FallingSky65)

This file contains the possible poker hands.
Hand is an abstract class that the other hands inherit from.

The hands:
- RoyalFlush
- StraightFlush
- FourOfAKind
- FullHouse
- Flush
- Straight
- ThreeOfAKind
- TwoPair
- OnePair
- HighCard

All of these hand types implement
- get_cards() to get the list of cards of the hand
- comparison overrides for comparing with other hands,
  greater hands are better hands

This file also contains the get_best_hand function, which
takes a list of 7 cards and outputs the best 5 card hand
from the 7 cards.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from .card import Card

intstr = int | str

class Hand(ABC):
    def __init__(self, hand_type : str, hand_ranking : int) -> None:
        super().__init__()
        self.hand_type : str = hand_type
        self.hand_ranking : int = hand_ranking

    @abstractmethod
    def get_cards(self) -> list[Card]:
        pass

    @abstractmethod
    def compare(self, other : Hand) -> int:
        # self < other -> negative
        # self = other -> 0
        # self > other -> positive
        return self.hand_ranking - other.hand_ranking

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Hand):
            return False
        return self.compare(value) == 0

    def __ne__(self, value: object, /) -> bool:
        return not self.__eq__(value)

    def __lt__(self, other: Hand) -> bool:
        return self.compare(other) < 0
    
    def __le__(self, other: Hand) -> bool:
        return self.compare(other) <= 0
    
    def __gt__(self, other: Hand) -> bool:
        return self.compare(other) > 0
    
    def __ge__(self, other: Hand) -> bool:
        return self.compare(other) >= 0

    def __repr__(self) -> str:
        return f'{self.hand_type}({self.__str__()})'

    def __str__(self) -> str:
        return ', '.join([str(c) for c in self.get_cards()])


class RoyalFlush(Hand):
    # royal flush identifiable by suit
    def __init__(self, suit : intstr) -> None:
        super().__init__('RoyalFlush', 9)
        self.suit : int = Card.suit2int(suit)

    def get_cards(self) -> list[Card]:
        return [
            Card(suit=self.suit, rank='A'),
            Card(suit=self.suit, rank='K'),
            Card(suit=self.suit, rank='Q'),
            Card(suit=self.suit, rank='J'),
            Card(suit=self.suit, rank='T'),
        ]

    def compare(self, other: Hand) -> int:
        # nothing additional needed, all royal flushes rank the same
        return super().compare(other)

class StraightFlush(Hand):
    # straight flush identifiable by
    #   suit
    #   highest ranking card
    def __init__(self, suit : intstr, high : intstr) -> None:
        super().__init__('StraightFlush', 8)
        self.suit : int = Card.suit2int(suit)
        self.high : int = Card.rank2int(high)
        # highest high is a K, ace would be royal flush
        # lowest high is a 5
        assert Card.rank2int('5') <= self.high <= Card.rank2int('K')

    def get_cards(self) -> list[Card]:
        # modulo 13 for the one case where Ace is the smallest card -> rank = -1
        return [Card(suit=self.suit, rank=(self.high - i)%13) for i in range(5)]

    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, StraightFlush)
        return self.high - other.high

class FourOfAKind(Hand):
    # four of a kind identifiable by
    #   rank of quad
    #   kicker
    def __init__(self, quad_rank : intstr, kicker : Card) -> None:
        super().__init__('FourOfAKind', 7)
        self.quad_rank : int = Card.rank2int(quad_rank)
        self.kicker : Card = kicker

    def get_cards(self) -> list[Card]:
        return [Card(suit=i, rank=self.quad_rank) for i in range(4)] + [self.kicker]
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, FourOfAKind)
        t1 : int = self.quad_rank - other.quad_rank
        if t1 != 0:
            return t1
        return self.kicker.rank - other.kicker.rank

class FullHouse(Hand):
    # full house identifiable by
    #   rank of triplet
    #   missing suit of triplet
    #   rank of pair
    #   pair suit 1
    #   pair suit 2
    def __init__(self, trip_rank : intstr, trip_missing_suit : intstr, pair_rank : intstr,
                 pair_suits : tuple[intstr, intstr]) -> None:
        super().__init__('FullHouse', 6)
        assert self.trip_rank != self.pair_rank
        self.trip_rank : int = Card.rank2int(trip_rank)
        self.trip_missing_suit : int = Card.suit2int(trip_missing_suit)
        self.pair_rank : int = Card.rank2int(pair_rank)
        self.pair_suits : list[int] = [Card.suit2int(pair_suits[0]), Card.suit2int(pair_suits[1])]
        assert self.pair_suits[0] != self.pair_suits[1]
        self.pair_suits.sort()

    def get_cards(self) -> list[Card]:
        cards : list[Card] = []

        for suit in range(4):
            if suit != self.trip_missing_suit:
                cards.append(Card(suit=suit, rank=self.trip_rank))
        cards.append(Card(suit=self.pair_suits[0], rank=self.pair_rank))
        cards.append(Card(suit=self.pair_suits[1], rank=self.pair_rank))

        return cards
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, FullHouse)
        t1 : int = self.trip_rank - other.trip_rank
        if t1 != 0:
            return t1
        return self.pair_rank - other.pair_rank

class Flush(Hand):
    # flush identifiable by 
    #   suit
    #   ranks of 5 cards
    def __init__(self, suit : intstr, ranks : list[int] | list[str]) -> None:
        super().__init__('Flush', 5)
        assert len(ranks) == 5
        self.suit : int = Card.suit2int(suit)
        self.ranks : list[int] = [Card.rank2int(rank) for rank in ranks]
        assert len(set(self.ranks)) == 5
        self.ranks.sort(reverse=True)

    def get_cards(self) -> list[Card]:
        return [Card(suit=self.suit, rank=rank) for rank in self.ranks]
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, Flush)
        t1 : int = self.ranks[0] - other.ranks[0]
        if t1 != 0:
            return t1
        t2 : int = self.ranks[1] - other.ranks[1]
        if t2 != 0:
            return t2
        t3 : int = self.ranks[2] - other.ranks[2]
        if t3 != 0:
            return t3
        t4 : int = self.ranks[3] - other.ranks[3]
        if t4 != 0:
            return t4
        return self.ranks[4] - other.ranks[4]

class Straight(Hand):
    # straight identifiable by 
    #   highest card
    #   suits of cards in descending rank
    def __init__(self, high : intstr, suits : list[intstr]) -> None:
        super().__init__('Straight', 4)
        assert len(suits) == 5
        self.high : int = Card.rank2int(high)
        assert Card.rank2int('5') <= self.high <= Card.rank2int('A')
        self.suits : list[int] = [Card.suit2int(suit) for suit in suits]

    def get_cards(self) -> list[Card]:
        # modulo 13 for the one case where Ace is the smallest card -> rank = -1
        return [Card(suit=self.suits[i], rank=(self.high - i)%13) for i in range(5)]
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, Straight)
        return self.high - other.high

class ThreeOfAKind(Hand):
    # three of a kind identifiable by 
    #   triplet rank
    #   triplet missing suit
    #   two kickers
    def __init__(self, trip_rank : intstr, trip_missing_suit : intstr, kicker1 : Card, kicker2 : Card) -> None:
        super().__init__('ThreeOfAKind', 3)
        assert kicker1.rank != trip_rank
        assert kicker2.rank != trip_rank
        assert kicker1 != kicker2
        self.trip_rank : int = Card.rank2int(trip_rank)
        self.trip_missing_suit : int = Card.suit2int(trip_missing_suit)
        self.kickers : list[Card] = [kicker1, kicker2]
        self.kickers.sort(key=lambda c: c.rank, reverse=True)

    def get_cards(self) -> list[Card]:
        cards : list[Card] = []

        for suit in range(4):
            if suit != self.trip_missing_suit:
                cards.append(Card(suit=suit, rank=self.trip_rank))
        cards.append(self.kickers[0])
        cards.append(self.kickers[1])

        return cards
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, ThreeOfAKind)
        t1 : int = self.trip_rank - other.trip_rank
        if t1 != 0:
            return t1
        t2 : int = self.kickers[0].rank - other.kickers[0].rank
        if t2 != 0:
            return t2
        return self.kickers[1].rank - other.kickers[1].rank

class TwoPair(Hand):
    # two of a kind identifiable by
    #   high pair rank and suits
    #   low pair rank and suits
    #   kicker
    def __init__(self, pair1_rank : intstr, pair1_suits : tuple[intstr, intstr],
                 pair2_rank : intstr, pair2_suits : tuple[intstr, intstr], kicker : Card) -> None:
        super().__init__('TwoPair', 2)
        r1 : int = Card.rank2int(pair1_rank)
        r2 : int = Card.rank2int(pair2_rank)
        assert r1 != r2
        assert r1 != kicker.rank
        assert r2 != kicker.rank
        if r1 > r2:
            self.high_pair_rank : int = r1
            self.high_pair_suits : list[int] = [Card.suit2int(s) for s in pair1_suits]
            self.high_pair_suits.sort()
            self.low_pair_rank : int = r2
            self.low_pair_suits : list[int] = [Card.suit2int(s) for s in pair2_suits]
            self.low_pair_suits.sort()
        else:
            self.high_pair_rank : int = r2
            self.high_pair_suits : list[int] = [Card.suit2int(s) for s in pair2_suits]
            self.high_pair_suits.sort()
            self.low_pair_rank : int = r1
            self.low_pair_suits : list[int] = [Card.suit2int(s) for s in pair1_suits]
            self.low_pair_suits.sort()
        self.kicker = kicker
        assert self.high_pair_suits[0] != self.high_pair_suits[1]
        assert self.low_pair_suits[0] != self.low_pair_suits[1]

    def get_cards(self) -> list[Card]:
        return [
            Card(suit=self.high_pair_suits[0], rank=self.high_pair_rank),
            Card(suit=self.high_pair_suits[1], rank=self.high_pair_rank),
            Card(suit=self.low_pair_suits[0], rank=self.low_pair_rank),
            Card(suit=self.low_pair_suits[1], rank=self.low_pair_rank),
            self.kicker
        ]
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, TwoPair)
        t1 : int = self.high_pair_rank - other.high_pair_rank
        if t1 != 0:
            return t1
        t2 : int = self.low_pair_rank - other.low_pair_rank
        if t2 != 0:
            return t2
        return self.kicker.rank - other.kicker.rank

class OnePair(Hand):
    # one pair identifiable by
    #   pair rank and suits
    #   three kickers
    def __init__(self, pair_rank : intstr, pair_suits : tuple[intstr, intstr], kickers : list[Card]) -> None:
        super().__init__('OnePair', 1)
        assert len(kickers) == 3
        self.pair_rank : int = Card.rank2int(pair_rank)
        assert self.pair_rank != kickers[0].rank
        assert self.pair_rank != kickers[1].rank
        assert self.pair_rank != kickers[2].rank
        assert kickers[0] != kickers[1] and kickers[0] != kickers[2] and kickers[1] != kickers[2]
        self.pair_suits : list[int] = [Card.suit2int(s) for s in pair_suits]
        assert self.pair_suits[0] != self.pair_suits[1]
        self.pair_suits.sort()
        self.kickers : list[Card] = kickers.copy()
        self.kickers.sort(key=lambda c: c.rank, reverse=True)

    def get_cards(self) -> list[Card]:
        return [
            Card(suit=self.pair_suits[0], rank=self.pair_rank),
            Card(suit=self.pair_suits[1], rank=self.pair_rank),
            self.kickers[0],
            self.kickers[1],
            self.kickers[2],
        ]
    
    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, OnePair)
        t1 : int = self.pair_rank - other.pair_rank
        if t1 != 0:
            return t1
        t2 : int = self.kickers[0].rank - other.kickers[0].rank
        if t2 != 0:
            return t2
        t3 : int = self.kickers[1].rank - other.kickers[1].rank
        if t3 != 0:
            return t3
        return self.kickers[2].rank - other.kickers[2].rank

class HighCard(Hand):
    # high card identifiable by 
    #   the cards :)
    def __init__(self, cards : list[Card]) -> None:
        super().__init__('HighCard', 0)
        assert len(cards) == 5
        assert len(set([c.rank for c in cards])) == 5
        self.cards : list[Card] = cards.copy()
        self.cards.sort(key=lambda c: c.rank, reverse=True)

    def get_cards(self) -> list[Card]:
        return self.cards.copy()

    def compare(self, other: Hand) -> int:
        base : int = super().compare(other)
        if base != 0:
            return base
        assert isinstance(other, HighCard)
        t1 : int = self.cards[0].rank - other.cards[0].rank
        if t1 != 0:
            return t1
        t2 : int = self.cards[1].rank - other.cards[1].rank
        if t2 != 0:
            return t2
        t3 : int = self.cards[2].rank - other.cards[2].rank
        if t3 != 0:
            return t3
        t4 : int = self.cards[3].rank - other.cards[3].rank
        if t4 != 0:
            return t4
        return self.cards[4].rank - other.cards[4].rank

# --------

def __has_card(cardlist : list[Card], card : Card) -> bool:
    return card.__hash__() in [c.__hash__() for c in cardlist]

def __get_card(cardlist : list[Card], rank : intstr) -> Card | None:
    for suit in range(4):
        card = Card(suit=suit, rank=Card.rank2int(rank))
        if __has_card(cardlist, card):
            return card
    return None

def __rank_count(cardlist : list[Card], rank : intstr) -> int:
    count = 0
    for card in cardlist:
        if card.rank == Card.rank2int(rank):
            count += 1
    return count

def __suit_count(cardlist : list[Card], suit : intstr) -> int:
    count = 0
    for card in cardlist:
        if card.suit == Card.suit2int(suit):
            count += 1
    return count

def __get_flush_suit(cardlist : list[Card]) -> int | None:
    if len(cardlist) < 5:
        return None
    if __suit_count(cardlist, 'S') >= 5:
        return 0
    if __suit_count(cardlist, 'H') >= 5:
        return 1
    if __suit_count(cardlist, 'C') >= 5:
        return 2
    if __suit_count(cardlist, 'D') >= 5:
        return 3
    return None

def get_best_hand(cardlist : list[Card]) -> Hand:
    assert len(cardlist) == 7
    
    flush_suit : int | None = __get_flush_suit(cardlist)

    if flush_suit is not None:
        # check for royal flush
        if (__has_card(cardlist, Card(suit=flush_suit, rank='A')) and
            __has_card(cardlist, Card(suit=flush_suit, rank='K')) and
            __has_card(cardlist, Card(suit=flush_suit, rank='Q')) and
            __has_card(cardlist, Card(suit=flush_suit, rank='J')) and
            __has_card(cardlist, Card(suit=flush_suit, rank='T'))):
            return RoyalFlush(flush_suit)

        # check for straight flush
        for high in range(Card.rank2int('K'), Card.rank2int('5'), -1):
            if all([__has_card(cardlist, Card(suit=flush_suit, rank=(high-i)%13)) for i in range(5)]):
                return StraightFlush(suit=flush_suit, high=high)

    # check for 4 of a kind
    rank_counts : list[int] = [__rank_count(cardlist, rank) for rank in range(13)]
    if any([rank_count == 4 for rank_count in rank_counts]):
        quad_rank : int = rank_counts.index(4)
        for kicker_rank in reversed(range(13)):
            if quad_rank == kicker_rank:
                continue
            kicker = __get_card(cardlist, kicker_rank)
            if kicker is not None:
                return FourOfAKind(quad_rank=quad_rank, kicker=kicker)
    assert not any([rank_count == 4 for rank_count in rank_counts])

    # check for full house
    if any([rank_count == 3 for rank_count in rank_counts]):
        trip_rank : int = len(rank_counts) - 1 - rank_counts[::-1].index(3)
        trip_missing_suit : int = -1
        for suit in range(4):
            if not __has_card(cardlist, Card(suit=suit, rank=trip_rank)):
                trip_missing_suit = suit
                break
        assert trip_missing_suit >= 0
        
        for pair_rank in reversed(range(13)):
            if trip_rank == pair_rank:
                continue
            if rank_counts[pair_rank] >= 2:
                pair_suits : list[int] = [card.suit for card in cardlist if card.rank == pair_rank]
                return FullHouse(trip_rank=trip_rank, trip_missing_suit=trip_missing_suit,
                         pair_rank=pair_rank, pair_suits=(pair_suits[0], pair_suits[1]))
    
    # check for flush
    if flush_suit is not None:
        ranks : list[int] = sorted([c.rank for c in cardlist if c.suit == flush_suit])[:5]
        return Flush(suit=flush_suit, ranks=ranks)

    # check for straight
    for high in range(Card.rank2int('A'), Card.rank2int('5'), -1):
        gets : list[Card | None]= [__get_card(cardlist, (high-i)%13) for i in range(5)]
        cards : list[Card] = [c for c in gets if c is not None] # holy jank
        if len(cards) == 5:
            return Straight(high=high, suits=[c.suit for c in cards])

    # check for three of a kind
    if any([rank_count == 3 for rank_count in rank_counts]):
        trip_rank : int = len(rank_counts) - 1 - rank_counts[::-1].index(3)
        trip_missing_suit : int = -1
        for suit in range(4):
            if not __has_card(cardlist, Card(suit=suit, rank=trip_rank)):
                trip_missing_suit = suit
                break
        assert trip_missing_suit >= 0

        kicker1 : Card | None = None
        for kicker1_rank in reversed(range(13)):
            if trip_rank == kicker1_rank:
                continue
            if rank_counts[kicker1_rank] >= 1:
                kicker1 = __get_card(cardlist, kicker1_rank)
                break
        assert kicker1 is not None

        kicker2 : Card | None = None
        for kicker2_rank in reversed(range(kicker1.rank)):
            if trip_rank == kicker2_rank:
                continue
            if rank_counts[kicker2_rank] >= 1:
                kicker2 = __get_card(cardlist, kicker2_rank)
                break
        assert kicker2 is not None

        return ThreeOfAKind(trip_rank=trip_rank, trip_missing_suit=trip_missing_suit, kicker1=kicker1, kicker2=kicker2)

    # check for pairs
    if any([rank_count == 2 for rank_count in rank_counts]):
        pair1_rank : int = len(rank_counts) - 1 - rank_counts[::-1].index(2)
        pair1_suits : list[int] = [card.suit for card in cardlist if card.rank == pair1_rank]
        for pair2_rank in reversed(range(pair1_rank)):
            if rank_counts[pair2_rank] == 2:
                # theres a two pair
                pair2_suits : list[int] = [card.suit for card in cardlist if card.rank == pair2_rank]
                
                kicker : Card | None = None
                for kicker_rank in reversed(range(13)):
                    if pair1_rank == kicker_rank or pair2_rank == kicker_rank:
                        continue
                    if rank_counts[kicker_rank] >= 1:
                        kicker = __get_card(cardlist, kicker_rank)
                        break
                assert kicker is not None

                return TwoPair(pair1_rank=pair1_rank, pair1_suits=(pair1_suits[0], pair1_suits[1]), pair2_rank=pair2_rank, pair2_suits=(pair2_suits[0], pair2_suits[1]), kicker=kicker)
        
        # theres no two pair, but theres a one pair, w/ 3 kickers
                
        kicker1 : Card | None = None
        for kicker1_rank in reversed(range(13)):
            if pair1_rank == kicker1_rank:
                continue
            if rank_counts[kicker1_rank] >= 1:
                kicker1 = __get_card(cardlist, kicker1_rank)
                break
        assert kicker1 is not None

        kicker2 : Card | None = None
        for kicker2_rank in reversed(range(kicker1.rank)):
            if pair1_rank == kicker2_rank:
                continue
            if rank_counts[kicker2_rank] >= 1:
                kicker2 = __get_card(cardlist, kicker2_rank)
                break
        assert kicker2 is not None
        
        kicker3 : Card | None = None
        for kicker3_rank in reversed(range(kicker2.rank)):
            if pair1_rank == kicker3_rank:
                continue
            if rank_counts[kicker3_rank] >= 1:
                kicker3 = __get_card(cardlist, kicker3_rank)
                break
        assert kicker3 is not None

        return OnePair(pair_rank=pair1_rank, pair_suits=(pair1_suits[0], pair1_suits[1]), kickers=[kicker1, kicker2, kicker3])

    # high card
    return HighCard(sorted(cardlist, key=lambda c: c.rank, reverse=True)[:5])

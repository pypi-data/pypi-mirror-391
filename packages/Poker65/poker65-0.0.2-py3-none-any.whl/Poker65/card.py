'''
Author: Daniel Li (FallingSky65)

Card has two attributes
    suit (int) : the suit of the card
        0 - spade
        1 - heart
        2 - club
        3 - diamond
    rank (int) : the rank of the card
         0 - 2
         1 - 3
         2 - 4
         3 - 5
         4 - 6
         5 - 7
         6 - 8
         7 - 9
         8 - 10
         9 - Jack
        10 - Queen
        11 - King
        12 - Ace

attributes can only be set upon construction

Card also contains two helper methods, for converting
possible string representations of the suit/rank into
the corresponding int.

rank2int(rank : int | str) -> int
suit2int(rank : int | str) -> int
'''

from dataclasses import dataclass

@dataclass(init=False, repr=False, frozen=True)
class Card():
    suit : int
    rank : int

    @staticmethod
    def suit2int(suit : int | str) -> int:
        if type(suit) is int:
            assert 0 <= suit < 4
            return suit
        elif type(suit) is str:
            assert len(suit) == 1 and suit in 'SHCD'
            return 'SHCD'.index(suit)
        else:
            raise TypeError
    
    @staticmethod
    def rank2int(rank : int | str) -> int:
        if type(rank) is int:
            assert 0 <= rank < 13
            return rank
        elif type(rank) is str:
            assert len(rank) == 1 and rank in '23456789TJQKA'
            return '23456789TJQKA'.index(rank)
        else:
            raise TypeError

    def __init__(self, suit : int | str, rank : int | str) -> None:
        object.__setattr__(self, 'suit', self.suit2int(suit))
        object.__setattr__(self, 'rank', self.rank2int(rank))

    def __repr__(self) -> str:
        return f'Card({self.__str__()})'

    def __str__(self) -> str:
        return '♠♡♣♢'[self.suit] + '23456789TJQKA'[self.rank]

    def __hash__(self) -> int:
        return self.suit * 13 + self.rank

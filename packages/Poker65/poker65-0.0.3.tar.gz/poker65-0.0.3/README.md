# Poker65
Python library for working with poker hands.

Functionality includes:
- creating card objects
- creating hand objects
- comparing poker hands
- getting the best poker hand from a list of 7 cards

## Installation
Install using pip:

```bash
pip install Poker65
```

## Example Usage

### Creating Cards

Cards store the suit and rank data as integers, but
the Card class has helper functions to convert strings
to the corresponding int.

Suits:
```py
from Poker65.card import Card
# int : str : meaning
#   0 : 'S' : spade
#   1 : 'H' : heart
#   2 : 'C' : club
#   3 : 'D' : diamond
suit : int = Card.suit2int('H') # 1
```

Ranks:
```py
from Poker65.card import Card
# int : str : meaning
#   0 : '2' : Two
#   1 : '3' : Three
#   2 : '4' : Four
#   3 : '5' : Five
#   4 : '6' : Six
#   5 : '7' : Seven
#   6 : '8' : Eight
#   7 : '9' : Nine
#   8 : 'T' : Ten
#   9 : 'J' : Jack
#  10 : 'Q' : Queen
#  11 : 'K' : King
#  12 : 'A' : Ace
rank : int = Card.rank2int('T') # 8
```

Cards can be created like so
```py
from Poker65.card import Card

cardWithInt = Card(suit=0, rank=0)

# creating a full deck of 52 cards
deck = []
for suit in 'SHCD': # spade, heart, club, diamond
    for rank in '23456789TJQKA': # ace is highest
        # Card constructor uses suit2int and rank2int
        Card(suit=suit, rank=rank)
```

Note that cards are immutable, suit and rank cannot be
modified after creating the Card.

### Creating Hands

All hand types are subclasses of the abstract class `Hand`,
and they all implement a `get_cards()` method that returns
the list of the 5 cards that make up the hand, and the hands
allow for comparison.
```py
from Poker65.card import Card
from Poker65.hands import *

hand1 = RoyalFlush(suit='H')
print(hand1) # ♡A, ♡K, ♡Q, ♡J, ♡T

hand2_cards = [
    Card('H', '6'),
    Card('S', 'A'),
    Card('C', '3'),
    Card('H', '9'),
    Card('H', 'K'),
]
hand2 = HighCard(cards=hand2_cards)
print(hand2) # ♠A, ♡K, ♡9, ♡6, ♣3

# hands can be compared, better hands are larger
print(hand1 > hand2) # True
print(hand1 == hand1) # True
print(hand1 == hand2) # False
print(hand1 <= hand2) # False
```

Hands can be created using their constructors.

RoyalFlush needs the suit of the hand.
```py
# ♢A, ♢K, ♢Q, ♢J, ♢T
print(RoyalFlush(suit='D'))
```

StraightFlush needs the suit and highest ranking card
```py
# ♣J, ♣T, ♣9, ♣8, ♣7
print(StraightFlush(suit='C', high='J'))
```

FourOfAKind needs the rank of the quad and the kicker card.
```py
# ♠5, ♡5, ♣5, ♢5, ♢2
print(FourOfAKind(quad_rank='5', kicker=Card('D', '2')))
```

FullHouse needs the rank of the triplet, the missing suit from
the triplet, the rank of the pair, and the two suits of the pair
```py 
# ♠6, ♡6, ♢6, ♡K, ♣K
print(FullHouse(
    trip_rank='6',
    trip_missing_suit='C',
    pair_rank='K',
    pair_suits=('C', 'H')
))
```

Flush needs the suit of the flush and the ranks of the cards.
```py 
# ♢J, ♢9, ♢8, ♢4, ♢3
print(Flush(suit='D', ranks=['8', 'J', '4', '9', '3']))
```

Straight needs the highest card and the suits of the cards, in
the order of descending rank.
```py 
# ♢T, ♠9, ♡8, ♢7, ♣6
print(Straight(high='T', suits=['D', 'S', 'H', 'D', 'C']))
```

ThreeOfAKind needs the triplet rank, the triplet's missing suit,
and the two kickers.
```py
# ♠Q, ♡Q, ♣Q, ♡9, ♠2
print(ThreeOfAKind(
    trip_rank='Q',
    trip_missing_suit='D',
    kicker1=Card('S', '2'),
    kicker2=Card('H', '9'),
))
```

TwoPair needs the ranks of the two pairs and the suits of the
cards in the two pairs, as well as the kicker.
```py 
# ♠J, ♡J, ♠3, ♣3, ♡2
print(TwoPair(
    pair1_rank='3', pair1_suits=('C', 'S'),
    pair2_rank='J', pair2_suits=('H', 'S'),
    kicker=Card('H', '2')
))
```

OnePair needs the pair rank and suits along with three kickers.
```py
# ♠T, ♡T, ♠8, ♡7, ♣4
print(OnePair(
    pair_rank='T', pair_suits=('S', 'H'),
    kickers=[Card('H', '7'), Card('S', '8'), Card('C', '4')]
))
```

HighCard needs the five cards.
```py
# ♢K, ♢Q, ♠7, ♠4, ♡3
print(HighCard(cards=[
    Card('D', 'Q'),
    Card('S', '7'),
    Card('D', 'K'),
    Card('S', '4'),
    Card('H', '3')
]))
```

### Using get_best_hand
`get_best_hand()` takes in a list of 7 cards, and returns
the best 5 card hand from the 7 cards.

```py
from Poker65.card import Card
from Poker65.hands import get_best_hand

# 4 of spades and 10 of clubs
hand = [Card(suit='S', rank='4'), Card(suit='C', rank='T')]

community_cards = [
    Card(suit='H', rank='9'), # 9 of hearts
    Card(suit='S', rank='2'), # 2 of spades
    Card(suit='C', rank='J'), # Jack of clubs
    Card(suit='H', rank='7'), # 7 of hearts
    Card(suit='D', rank='8'), # 8 of diamonds
]

# ♣J, ♣T, ♡9, ♢8, ♡7
print(get_best_hand(hand + community_cards))
# Straight(♣J, ♣T, ♡9, ♢8, ♡7) 
print(repr(get_best_hand(hand + community_cards)))
```

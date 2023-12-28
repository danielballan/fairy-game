import collections
import enum
import itertools
import random
import sys
from dataclasses import dataclass


class CardKind(enum.StrEnum):
    mr_winter = enum.auto()
    wand = enum.auto()
    golden_unicorn = enum.auto()
    rainbow_fairy = enum.auto()
    color_fairy = enum.auto()


class Color(enum.StrEnum):
    purple = enum.auto()
    pink = enum.auto()
    yellow = enum.auto()
    orange = enum.auto()


@dataclass(frozen=True)
class Card:
    kind: CardKind


@dataclass(frozen=True)
class ColorFairyCard(Card):
    color: Color


cards = (
    15 * [Card(kind=CardKind.mr_winter)]
    + 3 * [Card(kind=CardKind.wand)]
    + 4 * [Card(kind=CardKind.golden_unicorn)]
    + 3 * [Card(kind=CardKind.rainbow_fairy)]
    + 8 * [ColorFairyCard(kind=CardKind.color_fairy, color=Color.purple)]
    + 8 * [ColorFairyCard(kind=CardKind.color_fairy, color=Color.pink)]
    + 8 * [ColorFairyCard(kind=CardKind.color_fairy, color=Color.yellow)]
    + 8 * [ColorFairyCard(kind=CardKind.color_fairy, color=Color.orange)]
)
storm_colors = []
for member in Color:
    storm_colors.extend(11 * [member])


card_icons = {
    Card(kind=CardKind.mr_winter): "❄️  ",
    Card(kind=CardKind.wand): "🪄",
    Card(kind=CardKind.golden_unicorn): "🦄",
    Card(kind=CardKind.rainbow_fairy): "🌈",
    ColorFairyCard(kind=CardKind.color_fairy, color=Color.purple): "🟣 ",
    ColorFairyCard(kind=CardKind.color_fairy, color=Color.pink): "🔴 ",
    ColorFairyCard(kind=CardKind.color_fairy, color=Color.yellow): "🟡 ",
    ColorFairyCard(kind=CardKind.color_fairy, color=Color.orange): "🟠 ",
}
color_icons = {
    Color.purple: "🟣 ",
    Color.pink: "🔴 ",
    Color.yellow: "🟡 ",
    Color.orange: "🟠 ",
}


@dataclass
class State:
    turn: int
    hands: list[collections.Counter]
    board: dict[Color, int]
    jewels: set[Color]


def play(n_players):
    board = {member: 0 for member in Color}
    hands = [collections.Counter() for _ in range(n_players)]
    jewels = set()
    deck = cards.copy()
    storm_deck = storm_colors.copy()
    random.shuffle(deck)
    random.shuffle(storm_deck)
    for turn, player in enumerate(itertools.cycle(range(n_players))):
        hand = hands[player]
        card = deck.pop()
        if card.kind == CardKind.mr_winter:
            # Add frost.
            color = storm_deck.pop()
            board[color] += 1
        else:
            hand.update([card])
            # Check whether we can afford any jewels.
            num_rainbow_cards = hand[Card(kind=CardKind.rainbow_fairy)]
            can_buy = set()
            can_buy_with_rainbow = set()
            for color in set(Color) - jewels:
                if hand[ColorFairyCard(kind=CardKind.color_fairy, color=color)] >= 3:
                    can_buy.add(color)
                elif (
                    num_rainbow_cards
                    + hand[ColorFairyCard(kind=CardKind.color_fairy, color=color)]
                    >= 3
                ):
                    can_buy_with_rainbow.add(color)
            if can_buy:
                color = can_buy.pop()
                hand[card] -= 3
                jewels.add(color)
            elif can_buy_with_rainbow:
                num_rainbow_cards_to_spend = max(3 - hand[card], 3)
                hand[card] = 0
                hand[Card(kind=CardKind.rainbow_fairy)] -= num_rainbow_cards_to_spend
                jewels.add(color)
            while hand.total() > 5:
                # Discard at random
                hand.subtract([random.choice(list(hand.elements()))])
        yield (State(turn=turn, hands=hands, board=board, jewels=jewels))
        if max(board.values()) == 4:
            break  # loss
        if len(jewels) == 4:
            break  # win


def log(state):
    output = f"Turn {state.turn}\nJewels "
    output += "".join(color_icons[color] for color in state.jewels)
    output += "\nFlowers "
    output += (
        f"🟣 {state.board['purple'] * '❄️  '}"
        + f"    🔴 {state.board['pink'] * '❄️  '}"
        + f"    🟡 {state.board['yellow'] * '❄️  '}"
        + f"    🟠 {state.board['orange'] * '❄️  '}\nHands "
    )
    for hand in state.hands:
        output += "".join(card_icons[card] for card in hand.elements())
        output += "    "
    output += "\n"
    print(output, file=sys.stderr)


if __name__ == "__main__":
    n_players = int(sys.argv[1])
    if len(sys.argv) > 2:
        n_games = int(sys.argv[2])
    else:
        n_games = 1
    n_wins = 0
    for _ in range(n_games):
        for state in play(n_players):
            log(state)
            is_win = len(state.jewels) == 4
            if is_win:
                n_wins += 1
    print(f"{n_wins} wins / {n_games} games")

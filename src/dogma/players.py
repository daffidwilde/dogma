"""The player classes."""

import abc
import random


class BasePlayer:
    """A base player class to be inherited from."""

    def __init__(self, name):

        self.name = name
        self.role = None
        self.partner = None
        self.seen = None
        self.denounced = False

    def __repr__(self):

        class_name = self.__class__.__name__
        return f"{class_name}({self.name}, {self.role}, {self.denounced})"

    @abc.abstractmethod
    def nominate(self, players, ex_dean, ex_editor):
        """Placeholder for nominating an editor as dean."""

    @abc.abstractmethod
    def vote(self, nominee):
        """Placeholder for casting a vote on a potential editor."""

    @abc.abstractmethod
    def choose_cards_to_submit(self, choices, overrule_available=False):
        """Placeholder for how to select cards to keep and reject, or whether
        to instigate an overrule action."""

    @abc.abstractmethod
    def agree_to_overrule(self):
        """Placeholder for how to decide whether to accept a suggested
        overruling."""

    @abc.abstractmethod
    def denounce(self, players):
        """Placeholder for deciding who to denounce, if anyone."""


class RandomPlayer(BasePlayer):
    """A player who does everything at random."""

    def nominate(self, players):
        """Nominate an editor at random from the given players."""

        return random.choice(players)

    def vote(self, nominee):
        """Cast a vote at random."""

        return random.choice(("yes", "no"))

    def choose_cards_to_submit(self, choices, overrule_available=False):
        """Choose a card to reject at random."""

        overrule = False
        if overrule_available:
            overrule = self.agree_to_overrule()

        reject = random.choice(choices)
        choices.remove(reject)

        return choices, reject, overrule

    def agree_to_overrule(self):
        """Choose whether to agree to overrule at random."""

        return random.choice((True, False))

    def denounce(self, players):
        """Choose a random player to remove from the game from those
        presented."""

        return random.choice(players)

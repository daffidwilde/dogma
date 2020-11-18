"""The player classes."""

import abc


class Player:
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

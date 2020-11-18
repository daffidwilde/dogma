""" A class for playing randomly. """

import random

from dogma import Player


class Random(Player):
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

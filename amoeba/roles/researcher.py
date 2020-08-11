from amoeba.core import Player
from amoeba.abilities import *

class ResearcherShareKnowledge(ShareKnowledge):
    def choices(player, cards, players, **kwargs):
        chosen = yield 'teammate', [teammate for teammate in players if (teammate.city == player.city and teammate != player)]
        chosen = yield 'card', [card for card in cards if (card.type == 'city')]+[card for card in chosen['teammate'].cards if (card.type == 'city' and card.city == player.city)]

class Researcher(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ResearcherShareKnowledge, DiscoverCure, Ability]
        self.role_name = 'Researcher'

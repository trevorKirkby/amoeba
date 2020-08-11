from amoeba.core import Player
from amoeba.abilities import *

class SalvageEvent(Ability):
    name = 'Salvage Event Card'
    def choices(player, player_discard, **kwargs):
        yield 'card', [card for card in player_discard if (card.type == 'event' and card.reclaimed == False)]
    def execute(player, card):
        card.reclaimed = True
        player.cards.add(card)

class ContingencyPlanner(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ShareKnowledge, DiscoverCure, SalvageEvent, Ability]
        self.role_name = 'Contingency Planner'

from amoeba.core import Player
from amoeba.abilities import *

class OperationsBuildResearch(BuildResearch):
    def choices(player, **kwargs):
        if player.city.research: yield 'location', []
        yield 'location', [player.city]
    def execute(player, cards, location):
        location.research = True

class OperationsFlight(Ability):
    name = 'Operations Flight'
    def choices(player, cards, cities, **kwargs):
        if not player.city.research or player.flight_used: yield 'destination', []
        chosen = yield 'destination', [city for city in cities.values() if city != player.city]
        chosen = yield 'card', [card for card in cards if card.type == 'city']
    def execute(player, cards, destination, card):
        cards.remove(card)
        player.goto(destination)
        player.flight_used = True

class OperationsExpert(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, OperationsFlight, TreatDisease, OperationsBuildResearch, ShareKnowledge, DiscoverCure, Ability]
        self.role_name = 'Operations Expert'
        self.flight_used = False
    def begin_turn(self):
        self.flight_used = False

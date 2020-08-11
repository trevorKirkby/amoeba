from amoeba.core import Player
from amoeba.abilities import *

class ScientistDiscoverCure(DiscoverCure):
    def choices(player, cards, diseases, **kwargs):
        chosen = yield 'disease', [disease for disease in diseases.values() if (not disease.cured and len([card for card in cards if card.city.endemic_disease == disease])>=5)]
        for i in range(1,5): chosen = yield f'card {i}', [card for card in cards if (card.city.endemic_disease == disease and card not in chosen.values())]
    def execute(player, cards, **kwargs):
        for i in range(1,5): cards.remove(kwargs[f'card {i}'])
        kwargs['disease'].cured = True

class Scientist(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ShareKnowledge, ScientistDiscoverCure, Ability]
        self.role_name = 'Scientist'

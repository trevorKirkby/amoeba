from amoeba.core import Player
from amoeba.abilities import *

class MedicTreatDisease(TreatDisease):
    def execute(player, cards, disease):
        disease.remove(player.city,3)

class Medic(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, MedicTreatDisease, BuildResearch, ShareKnowledge, DiscoverCure, Ability] #Feels like there should be a way to do this just using inheritance...
        self.role_name = 'Medic'
    def goto(self, destination):
        super().goto(destination)
        for disease in destination.infections.keys():
            if disease.cured: disease.remove(destination, 3)

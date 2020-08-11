from amoeba.core import Player
from amoeba.abilities import *

class QuarantineSpecialist(Player):
    def __init__(self, name):
        super().__init__(name)
        self.role_name = 'Quarantine Specialist'
    def goto(self, destination):
        self.city.quarantined = False
        for neighbor in self.city.neighbors: neighbor.quarantined = False
        super().goto(destination)
        self.city.quarantined = True
        for neighbor in self.city.neighbors: neighbor.quarantined = True

from .. import amoeba_core
from .. import abilities

class Medic(amoeba_core.Player):
    def __init__(self, name, location):
        super().__init__(name, location)
        self.actions.remove(TreatDisease)
        self.actions.append(MedicTreatDisease)
    def move(self,destination):
        super().move(destination)
        for disease in destination.infections.keys():
            if disease.cured: disease.remove(destination, 3)

class MedicTreatDisease(TreatDisease):
    def execute(self, player, **kwargs):
        kwargs['disease'].remove(player.city,3)

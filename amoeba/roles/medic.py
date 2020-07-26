from .. import amoeba_core

class Medic(amoeba_core.Player):
    def __init__(self,location):
        super().__init__(location)
        self.color = ""
    def treat(self,disease):
        if self.city.infections[disease] == 0: return False
        self.city.infections[disease] = 0
        return True
    def move(self,destination):
        super().move(destination)
        for disease in destination.infections.keys():
            if disease.cured:
                self.treat(disease)

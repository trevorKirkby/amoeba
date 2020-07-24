from yaml import load

class World:
    def __init__(self,infection_rate):
        self.infection_rate = infection_rate
        self.outbreak_count = 0
        self.infection_deck = deque()
        self.player_deck = deque()

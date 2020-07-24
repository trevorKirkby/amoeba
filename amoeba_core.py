from collections import deque
from random import shuffle

class City:
    def __init__(self,name,endemic_disease,population,edges):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.edges = edges
        self.research = False
        self.infections = {}
        self.players = []

class Disease:
    def __init__(self,color,cubes_max):
        self.color = color
        self.cubes_remaining = cubes_max
        self.cured = False
        self.eradicated = False
    def outbreak(self, city):
        return
    def __hash__(self):
        return hash(self.color)
    def __eq__(self,other):
        return self.color==other.color

class Player:
    def __init__(self,location):
        self.city = location
        self.action_count = 0
        self.cards = deque()
    def move(self,destination):
        self.city = destination
    def drive(self,destination):
        if destination in self.city.edges:
            self.move(destination)
            return True
        return False
    def treat(self,disease):
        if self.city.infections[disease] == 0: return False
        if disease.cured:
            self.city.infections[disease] = 0
        else:
            self.city.infections[disease] -= 1
        return True

class World:
    def __init__(self,infection_rate):
        self.infection_rate = infection_rate
        self.outbreak_count = 0
        self.infection_deck = deque()
        self.infection_discard = deque()
        self.player_deck = deque()
        self.player_discard = deque()
        self.turn_rotation = deque()
    def epidemic(self):
        return

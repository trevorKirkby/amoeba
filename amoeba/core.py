from collections import deque
from random import shuffle, choice

class City:
    def __init__(self, name, population, endemic_disease, world):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.world = world
        self.neighbors = []
        self.research = False
        self.infections = {}
        self.players = []
    def infect(self, disease, amount):
        self.infections[disease] += amount
        if self.infections[disease] > 3:
            self.infections[disease] = 3
            self.outbreak(disease)
    def outbreak(self, disease):
        world.outbreak_count += 1
        for city in self.neighbors: city.infect(disease, 1)

class Disease:
    def __init__(self, color, cubes_max):
        self.color = color
        self.cubes_remaining = cubes_max
        self.cured = False
        self.eradicated = False
    def __hash__(self):
        return hash(self.color)
    def __eq__(self,other):
        return self.color == other.color

class Player:
    def __init__(self, location):
        self.city = location
        self.action_count = 0
        self.cards = deque()
    def move(self, destination):
        self.city = destination
    def drive(self,destination):
        if destination in self.city.edges:
            self.move(destination)
            return True
        return False
    def treat(self,disease):
        if self.city.infections[disease] == 0: return False
        if disease.cured: self.city.infections[disease] = 0
        else: self.city.infections[disease] -= 1
        return True

class World:
    def __init__(self, infection_rates, player_draw_rate):
        self.infection_rates = infection_rates
        self.player_draw_rate = player_draw_rate
        self.infection_counter = 0
        self.outbreak_count = 0
        self.infection_deck = deque()
        self.infection_discard = deque()
        self.player_deck = deque()
        self.player_discard = deque()
        self.turn_rotation = deque()
        self.diseases = {}
        self.cities = {}
    def add_disease(self, disease):
        self.diseases[disease.color] = disease
    def add_city(self, city):
        self.cities[city.name] = city
    def add_edge(self, city1, city2):
        city1 = self.cities[city1]
        city2 = self.cities[city2]
        city1.neighbors.append(city2)
        city2.neighbors.append(city1)
    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.infect(target_city.endemic_disease, 3)
        self.infection_discard.append(target_city)
        random.shuffle(self.infection_discard) #Intensify
        self.infection_deck.extend(self.infection_discard)
        self.infection_discard.clear()
    def infect(self):
        for i in range(infection_rates[infection_counter]):
            target_city = self.infection_deck.pop()
            target_city.infect(target_city.endemic_disease, 1)
            self.infection_discard.append(target_city)

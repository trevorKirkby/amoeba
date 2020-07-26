from collections import deque, defaultdict
from random import shuffle, choice

class City:
    def __init__(self, name, population, endemic_disease):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.neighbors = []
        self.research = False
        self.infections = defaultdict(int)
        self.players = []
    def infect(self, disease, amount):
        self.infections[disease] += amount
        if self.infections[disease] > 3:
            self.infections[disease] = 3
            self.outbreak(disease)
    def outbreak(self, disease):
        for city in self.neighbors: city.infect(disease, 1)

class Disease:
    def __init__(self, color, cubes_max):
        self.color = color
        self.cubes_remaining = cubes_max
        self.cured = False
        self.eradicated = False
    def take(self, n=1):
        if self.cubes_remaining < n:
            raise RuntimeError(f'GAME OVER: no more {self.color} disease cubes left.')
        self.cubes_remaining -= n
    def replace(self, n=1):
        self.cubes_remaining += n
    def __hash__(self):
        return hash(self.color)
    def __eq__(self,other):
        return self.color == other.color

class Player:
    def __init__(self, name, location):
        self.name = name
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
    def __init__(self, config):
        self.diseases = {}
        self.cities = {}
        for color in config["cities"]:
            self.diseases[color] = Disease(color, config["cubes_per_color"])
            for name in config["cities"][color]:
                self.cities[name] = City(name, 0, color)
        for name1, name2 in config["edges"]:
            city1 = self.cities[name1]
            city2 = self.cities[name2]
            city1.neighbors.append(city2)
            city2.neighbors.append(city1)
        self.config = config

    def start(self, num_players):
        if num_players > len(self.config['initial_city_cards']) or self.config['initial_city_cards'][num_players - 1] < 0:
            raise ValueError(f'Invalid number of players: {num_players}.')
        # Place initial research centers.
        self.research = []
        for name in self.config['start_research']:
            city = self.cities[name]
            city.research = True
            self.research.append(city)
        # Initialize infections.
        self.infection_counter = 0
        self.outbreak_count = 0
        self.infection_deck = deque(self.cities.keys())
        shuffle(self.infection_deck)
        self.infection_discard = deque()
        for n in self.config['initial_infections']:
            self.draw_infection_card(n)
        # Initialize the player deck.
        self.player_deck = deque(self.cities.keys())
        shuffle(self.player_deck)
        self.player_discard = deque()
        # Initialize the players.
        self.players = []
        for i in range(num_players):
            name = f'Player-{i+1}'
            player = Player(name, self.cities[self.config['start_city']])
            for j in range(self.config['initial_city_cards'][num_players]):
                self.next_card(player)
            self.players.append(player)

    def next_card(self, player):
        card = self.player_deck.pop()
        if not card:
            raise RuntimeError('GAME OVER: no more player cards.')
        self.player_discard.append(card)
        player.cards.append(card)
        print(f'Player {player.name} draws {card}.')

    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.infect(target_city.endemic_disease, 3)
        self.infection_discard.append(target_city)
        random.shuffle(self.infection_discard) #Intensify
        self.infection_deck.extend(self.infection_discard)
        self.infection_discard.clear()

    def infect_city(self, city, color):
        print(f'infecting {city.name}.')
        if city.infections[color] < self.config['outbreak_threshold']:
            self.diseases[color].take()
            city.infections[color] += 1
        else:
            # Outbreak!
            print(f'Outbreak in {city_name}.')
            if self.outbreak_counter == self.config['max_outbreaks']:
                raise RuntimeError('GAME OVER: reached max infections.')
            for neighbor in city.neighbors:
                self.infect_city(neighor, color)

    def draw_infection_card(self, infections=1):
        target_city = self.infection_deck.pop()
        if target_city is None:
            raise RuntimeError('GAME OVER: no more infection cards.')
        self.infection_discard.append(target_city)
        target_city = self.cities[target_city]
        for i in range(infections):
            self.infect_city(target_city, target_city.endemic_disease)

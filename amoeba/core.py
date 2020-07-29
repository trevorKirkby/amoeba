from collections import deque, Counter
from random import shuffle, choice

from amoeba.abilities import *
from amoeba.cards import *

class City:
    def __init__(self, name, population, endemic_disease):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.neighbors = []
        self.players = []
        self.research = False
        self.infections = Counter()

class Player:
    def __init__(self, name, location):
        self.name = name
        self.city = location
        self.action_count = 0
        self.cards = deque()
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ShareKnowledge, DiscoverCure]

    def move(self, destination):
        self.city = destination

class Disease:
    def __init__(self, color, cubes_max, outbreak_threshold):
        self.color = color
        self.cubes_remaining = cubes_max
        self.outbreak_threshold = outbreak_threshold
        self.cured = False
        self.eradicated = False
        self.outbreak_count = 0

    def __hash__(self):
        return hash(self.color)

    def infect(self, city, amount=1):
        for i in range(amount):
            print(f'infecting {city.name}.')
            if city.infections[self] == self.outbreak_threshold:
                self.outbreak(city)
                break
            if self.cubes_remaining == 0:
                raise RuntimeError(f'GAME OVER: no more {self.color} disease cubes left.')
            self.cubes_remaining -= 1
            city.infections[self] += 1

    def remove(self, city, amount=1):
        for i in range(amount):
            if city.infections[self] == 0: break
            print(f'treating {city.name}.')
            self.cubes_remaining += 1
            city.infections[self] -= 1

    def outbreak(self, city):
        print(f'Outbreak in {city_name}.')
        self.outbreak_count += 1
        for neighbor in city.neighbors:
            self.infect(neighbor, 1)

class World:
    def __init__(self, config):
        self.diseases = {}
        self.cities = {}
        for color in config["cities"]:
            self.diseases[color] = Disease(color, config['cubes_per_color'], config['outbreak_threshold'])
            for name in config["cities"][color]:
                self.cities[name] = City(name, 0, self.diseases[color])
        for name1, name2 in config["edges"]:
            city1 = self.cities[name1]
            city2 = self.cities[name2]
            city1.neighbors.append(city2)
            city2.neighbors.append(city1)
        self.config = config

    def start(self, num_players, num_epidemics):
        if num_players > len(self.config['initial_city_cards']) or self.config['initial_city_cards'][num_players - 1] < 0:
            raise ValueError(f'Invalid number of players: {num_players}.')
        # Place initial research centers.
        for name in self.config['start_research']:
            city = self.cities[name]
            city.research = True
        # Initialize infections.
        self.infection_counter = 0
        self.infection_deck = deque(self.cities.values())
        shuffle(self.infection_deck)
        self.infection_discard = deque()
        for n in self.config['initial_infections']:
            self.draw_infection_card(n)
        # Initialize the player deck.
        self.player_deck = deque([CityCard(city) for city in self.cities.values()])
        shuffle(self.player_deck)
        self.player_discard = deque()
        # Initialize the players.
        self.players = []
        for i in range(num_players):
            name = f'Player-{i+1}'
            player = Player(name, self.cities[self.config['start_city']])
            for j in range(self.config['initial_city_cards'][num_players]):
                self.draw_player_card(player)
            self.players.append(player)
        # Initialize epidemics.
        cards_list = list(self.player_deck)
        bucket_size = round(len(cards_list) / num_epidemics)
        buckets = [cards_list[i:i+bucket_size] for i in range(0, len(cards_list), bucket_size)]
        buckets = [bucket+[EpidemicCard()] for bucket in buckets]
        for bucket in buckets: shuffle(bucket)
        self.player_deck = deque([card for bucket in buckets for card in bucket])

    def draw_infection_card(self, infections=1):
        target_city = self.infection_deck.pop()
        target_city.endemic_disease.infect(target_city, infections)
        self.infection_discard.append(target_city)
        if sum([disease.outbreak_count for disease in self.diseases.values()]) > self.config['max_outbreaks']:
            raise RuntimeError('GAME OVER: reached max outbreaks.')

    def draw_player_card(self, player):
        card = self.player_deck.pop()
        if not card:
            raise RuntimeError('GAME OVER: no more player cards.')
        print(f'Player {player.name} draws {card.name}.')
        if card.type == 'epidemic':
            self.epidemic()
            return
        self.player_discard.append(card)
        player.cards.append(card)

    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.endemic_disease.infect(target_city, 3)
        self.infection_discard.append(target_city)
        shuffle(self.infection_discard) #Intensify
        self.infection_deck.extend(self.infection_discard)
        self.infection_discard.clear()

    def player_turn(self, player):
        return

    def player_discard(self, player):
        return

    def main_loop(self):
        while not self.game_over:
            active_player = self.players.pop()
            player_turn(active_player)
            for i in range(self.config['city_cards_per_turn']):
                self.draw_player_cards(active_player)
            player_discard(active_player)
            for i in range(config['infection_cards_per_turn'][self.infection_counter]):
                self.draw_infection_card()
            self.players.appendleft(active_player)

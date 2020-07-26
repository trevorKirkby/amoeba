from collections import deque, Counter
from random import shuffle, choice

class City:
    def __init__(self, name, population, endemic_disease):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.neighbors = []
        self.research = False
        self.infections = Counter
        self.players = []
    def infect(self, disease, amount):
        for i in range(amount):
            if self.infections[disease] == 3:
                self.outbreak(disease)
                break
            self.infections[disease] += 1
            disease.cubes_remaining -= 1
            if disease.cubes_remaining < 0: world.game_over = -1
    def treat(self, disease, amount):
        for i in range(amount):
            if self.infections[disease] == 0: break
            self.infections[disease] -= 1
            disease.cubes_remaining += 1
    def outbreak(self, disease):
        world.outbreak_count += 1
        if world.outbreak_count > world.config[max_outbreaks]: world.game_over = -1
        for city in self.neighbors: city.infect(disease, 1)
    def build_research(self, player):
        if world.research_stations_count == world.config["research_centers"]:
            pass #call UI code to let player choose which research station to relocate
        else:
            self.research = True
            world.research_stations_count += 1

class Disease:
    def __init__(self, color, cubes_max):
        self.color = color
        self.cubes_remaining = cubes_max
        self.cured = False
        self.eradicated = False
    def __hash__(self):
        return hash(self.color)
    def __eq__(self, other):
        return self.color == other.color

class Player:
    def __init__(self, location):
        self.city = location
        self.action_count = 0
        self.cards = deque()
    def move(self, destination):
        self.city = destination
    def drive(self, destination):
        if destination in self.city.edges:
            self.move(destination)
            return True
        return False
    def shuttle_flight(self, destination):
        if self.city.research and destination.research:
            self.move(destination)
            return True
        return False
    def direct_flight(self, destination):
        if self.cards.count(destination):
            self.move(destination)
            self.cards.remove(destination)
            return True
        return False
    def charter_flight(self, destination):
        if self.cards.count(self.city):
            self.move(destination)
            self.cards.remove(self.city)
            return True
        return False
    def treat(self, disease):
        if self.city.infections[disease] == 0: return False
        if disease.cured: self.city.treat(disease, 3)
        else: self.city.treat(disease, 1)
        return True
    def share_knowledge(self, other, citycard):
        if self.city != citycard: return False
        if self.cards.count(citycard):
            self.cards.remove(citycard)
            other.cards.append(citycard)
            return True
        if other.cards.count(citycard):
            other.cards.remove(citycard)
            self.cards.append(citycard)
            return True
        return False
    def build_research(self):
        if self.city.research: return False
        if self.cards.count(self.city):
            self.city.build_research(self)
            self.cards.remove(self.city)
            return True
        return False
    def discover_cure(self, disease):
        available = [card for card in self.cards if card.city.endemic_disease == disease]
        if len(available) > 5:
            pass #call UI code to let player choose which 5 cards to spend to discover the cure
        if len(available) == 5:
            for card in available: self.cards.remove(card)
            disease.cured = True
            if all([strain.cured for strain in world.diseases.values()]): world.game_over = 1
            return True
        return False

class PlayerCard:
    def __init__(self, type):
        self.type = type
    def __eq__(self, other):
        return False

class CityCard(PlayerCard):
    def __init__(self, city):
        super.__init__("city")
        self.city = city
    def __eq__(self, other):
        return (self.city == other.city or self.city == other)

class EventCard(PlayerCard):
    def __init__(self):
        super.__init__("event")
    def play(self, player):
        return

class EpidemicCard(PlayerCard):
    def __init__(self):
        super.__init__("epidemic")

class World:
    def __init__(self, config):
        self.diseases = {}
        self.cities = {}
        for color in config["cities"]:
            self.diseases[color] = Disease(color, config["constants"]["cubes_per_color"])
            for name in config["cities"][color]:
                self.cities[name] = City(name, 0, color)
        for name1, name2 in config["edges"]:
            city1 = self.cities[name1]
            city2 = self.cities[name2]
            city1.neighbors.append(city2)
            city2.neighbors.append(city1)
        self.config = config
        self.infection_counter = 0
        self.outbreak_count = 0
        self.research_stations_count = 0
        self.infection_deck = deque()
        self.infection_discard = deque()
        self.player_deck = deque()
        self.player_discard = deque()
        self.players = deque()
        self.game_over = 0 #0 = game not over, 1 = game won, -1 = game lost
    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.infect(target_city.endemic_disease, 3)
        self.infection_discard.append(target_city)
        random.shuffle(self.infection_discard) #Intensify
        self.infection_deck.extend(self.infection_discard)
        self.infection_discard.clear()
    def infect(self):
        for i in range(config['infection_cards_per_turn'][self.infection_counter]):
            target_city = self.infection_deck.pop()
            target_city.infect(target_city.endemic_disease, 1)
            self.infection_discard.append(target_city)
    def draw_player_cards(self, player):
        for i in range(config["city_cards_per_turn"]):
            if not self.player_deck.len():
                self.game_over = -1
                return
            card = self.player_deck.pop()
            if card.type == "epidemic": epidemic()
            else: player.cards.append(card)
    def main_loop(self):
        while not self.game_over:
            active_player = self.players.pop()
            #call UI code to let player take a turn
            if game_over: break #no point in drawing more cards if the game just ended
            self.draw_player_cards(self, active_player)
            if game_over: break
            #call UI code to let player decide which cards to discard
            self.infect()
            self.players.appendleft(active_player)
        return self.game_over

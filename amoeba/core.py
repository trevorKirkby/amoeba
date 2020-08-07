from collections import deque, Counter
from random import shuffle, choice

from amoeba.abilities import *
from amoeba.cards import *
import amoeba.robo as robo

class City:
    def __init__(self, name, population, endemic_disease):
        self.name = name
        self.endemic_disease = endemic_disease
        self.population = population
        self.neighbors = []
        self.players = []
        self.research = False
        self.outbreaking = False
        self.infections = Counter()

class Player:
    def __init__(self, name, location):
        self.name = name
        self.city = location
        self.action_count = 0
        self.cards = deque()
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ShareKnowledge, DiscoverCure, Ability]

    def move(self, destination):
        self.city = destination

    def describe(self):
        city_status = [f'{d.color} {n}' for d, n in self.city.infections.items()] or ['no disease']
        if self.city.research:
            city_status.append('research center')
        my_cards = ', '.join([C.name for C in self.cards])
        return f'in {self.city.name} ({", ".join(city_status)}) with cards: {my_cards}.'

class Disease:
    def __init__(self, color, cubes_max, outbreak_threshold):
        self.name = color
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
            if city.infections[self] == self.outbreak_threshold:
                self.outbreak(city)
                break
            if self.cubes_remaining == 0:
                raise RuntimeError(f'GAME OVER: no more {self.name} disease cubes left.')
            self.cubes_remaining -= 1
            robo.do(f"{self.color} cube from bin to {city.name}")
            city.infections[self] += 1

    def remove(self, city, amount=1):
        for i in range(amount):
            if city.infections[self] == 0: break
            print(f'Treating {city.name}.')
            self.cubes_remaining += 1
            city.infections[self] -= 1

    def outbreak(self, city):
        print(f'Outbreak in {city.name}.')
        self.outbreak_count += 1
        city.outbreaking = True
        for neighbor in city.neighbors:
            if not neighbor.outbreaking:
                self.infect(neighbor, 1)
        city.outbreaking = False

class World:
    def __init__(self, config):
        self.diseases = {}
        self.cities = {}
        for color in config["cities"]:
            self.diseases[color] = Disease(color, config['cubes_per_color'], config['outbreak_threshold'])
            robo.enable(color + " cube", "bin")
            for name in config["cities"][color]:
                self.cities[name] = City(name, 0, self.diseases[color])
        robo.enable("research center", "bin")
        for city in self.cities:
            robo.enable("research center", city)
            robo.enable(city, "infection deck")
            robo.enable(city, "infection discard")
            robo.enable(city, "player deck")
            robo.enable(city, "player discard")
            for color in config["cities"]:
                robo.enable(color + " cube", city)
        for name1, name2 in config["edges"]:
            city1 = self.cities[name1]
            city2 = self.cities[name2]
            city1.neighbors.append(city2)
            city2.neighbors.append(city1)
        self.config = config

    def start(self, num_players, num_epidemics):
        if num_players > len(self.config['initial_city_cards']) or self.config['initial_city_cards'][num_players - 1] < 0:
            raise ValueError(f'Invalid number of players: {num_players}.')
        # Define tasks associated with players.
        for i in range(num_players):
            robo.enable(f"player {i+1}", "bin")
            for city in self.cities:
                robo.enable(f"player {i+1}", city)
                robo.enable(city, f"player {i+1}")
        # Place initial research centers.
        for name in self.config['start_research']:
            city = self.cities[name]
            robo.do(f"research center from bin to {city.name}")
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
        self.players = deque()
        for i in range(num_players):
            name = f'player {i+1}'
            player = Player(name, self.cities[self.config['start_city']])
            robo.do(f"player {i+1} from bin to {player.city.name}")
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
        # Start the game.
        self.main_loop()

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
        if card.type == 'epidemic':
            self.epidemic()
            return
        robo.do(f"{card.name} from player deck to {player.name}")
        player.cards.append(card)

    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.endemic_disease.infect(target_city, 3)
        self.infection_discard.append(target_city)
        shuffle(self.infection_discard) #Intensify
        self.infection_deck.extend(self.infection_discard)
        self.infection_discard.clear()

    def pick(self, choice_description, pick_from, cancel=False): #Helper method for getting text input.
        picked = None
        while not picked:
            print(f'Choose {choice_description}:')
            for i in range(len(pick_from)):
                print(f'\t ({i}) {pick_from[i].name}')
            if cancel: print(f'\t ({len(pick_from)}) Cancel')
            user_pick = input('Pick one: ')
            try:
                user_pick = int(user_pick)
                if cancel and user_pick == len(pick_from): return 'Cancel'
                picked = pick_from[user_pick]
            except (ValueError, KeyError) as e:
                print('Must be specified as one of the listed numbers.')
        return picked

    def player_turn(self, player): #Quick text-based interface for player turns.
        print(f'\n{player.name}\'s turn.')
        player.action_count = self.config['actions_per_turn']
        while player.action_count:
            print('You are', player.describe())
            action = self.pick('an action', player.actions)
            choices = action.choices(player, **self.__dict__) #Actions pretty much happen on a world-level and can view the full world state in order to decide what actions are legal and what isn't.
            viable = True
            canceled = False
            chosen = {}
            choice = next(choices)
            while choice:
                if not choice[1]:
                    viable = False
                    break
                latest_chosen = self.pick(choice[0],choice[1],cancel=True)
                if latest_chosen == 'Cancel':
                    canceled = True
                    break
                chosen.update({choice[0]:latest_chosen})
                try: choice = choices.send(chosen)
                except StopIteration: break
            if canceled:
                continue
            if not viable:
                print('That action can\'t be taken right now.')
                continue
            action.execute(player, **chosen)
            player.action_count -= 1
            self.check_win()
        print(f'{player.name} has used all their actions.')

    def check_discard(self, player):
        while len(player.cards) > self.config['max_cards_per_player']:
            print(f'{player.name} has too many cards.')
            player.cards.remove(self.pick('a card to discard', player.cards))

    def check_win(self):
        if all([disease.cured for disease in self.diseases.values()]):
            raise RuntimeError('You won!!!')

    def main_loop(self):
        while True:
            active_player = self.players.pop()
            self.player_turn(active_player)
            for i in range(self.config['city_cards_per_turn']):
                self.draw_player_card(active_player)
            self.check_discard(active_player)
            for i in range(self.config['infection_cards_per_turn'][self.infection_counter]):
                self.draw_infection_card()
            self.players.appendleft(active_player)

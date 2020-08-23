from collections import deque, Counter
import random

from amoeba.abilities import *
from amoeba.cards import *
from amoeba.roles.roles_list import roles_list, load_role
import amoeba.robo as robo

class City:
    """A City object records the cubes, players and research centers at its location,
    and knows what other cities it is connected to.
    """
    def __init__(self, data, endemic_disease):
        self.name = data["name"]
        self.geopoint = data["geo"]
        self.population = data["pop"]
        self.endemic_disease = endemic_disease
        self.neighbors = []
        self.research = False
        self.outbreaking = False
        self.quarantined = False
        self.infections = Counter()
        City._registry[self.name] = self

    _registry = {}

    @staticmethod
    def find(name):
        if name not in City._registry:
            raise ValueError(f'Got invalid request for unknown city: "{name}".')
        return City._registry[name]

class Player:
    """A Player object records its current location, player cards and turn progress.
    """
    def __init__(self, name):
        self.name = name
        self.city = None
        self.action_count = 0
        self.cards = deque()
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, TreatDisease, BuildResearch, ShareKnowledge, DiscoverCure, Ability]
        self.role_name = 'Ordinary Person'
        robo.listen(self.move, self.name)

    def goto(self, destination): #Because somebody got rid of the old "move" method and then stole the name to use for something else >:[
        robo.do(self.name, self.city.name, destination.name)

    def begin_turn(self):
        return

    def move(self, what, src, dst):
        assert what == self.name
        self.city = City.find(dst)

    def describe(self):
        city_status = [f'{d.color} {n}' for d, n in self.city.infections.items()] or ['no disease']
        if self.city.research:
            city_status.append('research center')
        my_cards = ', '.join([C.name for C in self.cards])
        return f'the {self.role_name} in {self.city.name} ({", ".join(city_status)}) with cards: {my_cards}.'

class Disease:
    """A Disease object manages the cubes of a single color and is responsible for
    infections, outbreaks, and detecting if the game ends because all cubes are
    already on the board.
    """
    def __init__(self, color, cubes_max, outbreak_threshold):
        self.name = color
        self.color = color
        self.cubes_remaining = cubes_max
        self.outbreak_threshold = outbreak_threshold
        self.cured = False
        self.eradicated = False
        self.outbreak_count = 0
        # Dispatch any moves of our color cubes to our move mehod.
        robo.listen(self.move, f'{self.color} cube')

    def __hash__(self):
        return hash(self.color)

    def move(self, what, src, dst):
        assert what == f'{self.color} cube'
        if src == 'bin':
            if self.cubes_remaining == 0:
                raise RuntimeError(f'GAME OVER: no more {self.name} disease cubes left.')
            self.cubes_remaining -= 1
            City.find(dst).infections[self] += 1
        elif dst == 'bin':
            self.cubes_remaining += 1
            City.find(src).infections[self] -= 1
        else:
            raise RuntimeError('Invalid Disease move from {src} to {dst}.')

    def infect(self, city, amount=1):
        if city.quarantined: return
        for i in range(amount):
            if city.infections[self] == self.outbreak_threshold:
                self.outbreak(city)
                break
            robo.do(f"{self.color} cube", "bin", city.name)

    def remove(self, city, amount=1):
        for i in range(amount):
            if city.infections[self] == 0: break
            print(f'Treating {city.name}.')
            robo.do(f"{self.color} cube", city.name, "bin")

    def outbreak(self, city):
        print(f'Outbreak in {city.name}.')
        self.outbreak_count += 1
        city.outbreaking = True
        for neighbor in city.neighbors:
            if not neighbor.outbreaking:
                self.infect(neighbor, 1)
        city.outbreaking = False

class World:
    """The World object manages the City, Player and Disease objects in a game, and
    implements the game turn mechanics.
    """
    def __init__(self, config):
        self.diseases = {}
        self.cities = {}
        for color in config["cities"]:
            self.diseases[color] = Disease(color, config['cubes_per_color'], config['outbreak_threshold'])
            robo.enable(color + " cube", "bin")
            for citydata in config["cities"][color]:
                city = City(citydata, self.diseases[color])
                self.cities[city.name] = city
        self.research_centers_in_bin = config["research_centers"]
        robo.enable("research center", "bin")
        for city in self.cities:
            robo.enable("research center", city)
            robo.enable(city + " infection card", "infection deck")
            robo.enable(city + " infection card", "infection discard")
            robo.enable(city + " player card", "player deck")
            robo.enable(city + " player card", "player discard")
            for color in config["cities"]:
                robo.enable(color + " cube", city)
        for name1, name2 in config["edges"]:
            city1 = self.cities[name1]
            city2 = self.cities[name2]
            city1.neighbors.append(city2)
            city2.neighbors.append(city1)
        self.config = config
        # Dispatch research center tasks.
        robo.listen(self.move_research, "research center")

    def move_research(self, what, src, dst):
        assert what == 'research center' and dst != 'bin'
        City.find(dst).research = True
        if src != 'bin':
            City.find(src).research = False

    def start(self, num_players, num_epidemics, seed):
        self.gen = random.Random(seed)
        if num_players > len(self.config['initial_city_cards']) or self.config['initial_city_cards'][num_players - 1] < 0:
            raise ValueError(f'Invalid number of players: {num_players}.')
        # Define tasks associated with players.
        for i in range(num_players):
            robo.enable(f"player {i+1}", "bin")
            for city in self.cities:
                robo.enable(f"player {i+1}", city)
                robo.enable(city + " player card", f"player {i+1} hand")
        # Place initial research centers.
        for name in self.config['start_research']:
            if self.research_centers_in_bin == 0:
                raise RuntimeError('Not enough research centers for initial setup!')
            robo.do("research center", "bin", name)
        # Initialize infections.
        self.infection_counter = 0
        self.infection_deck = deque(self.cities.values())
        self.gen.shuffle(self.infection_deck)
        self.infection_discard = deque()
        for n in self.config['initial_infections']:
            self.draw_infection_card(n)
        # Initialize the player deck.
        self.player_deck = deque([CityCard(city) for city in self.cities.values()])
        self.gen.shuffle(self.player_deck)
        self.player_discard = deque()
        # Initialize the players.
        self.players = deque()
        self.gen.shuffle(roles_list)
        for i in range(num_players):
            name = f'player {i+1}'
            Role = load_role(roles_list.pop())
            player = Role(name)
            robo.do(f"player {i+1}", "bin", self.config['start_city'])
            for j in range(self.config['initial_city_cards'][num_players]):
                self.draw_player_card(player)
            self.players.append(player)
        # Initialize epidemics.
        cards_list = list(self.player_deck)
        bucket_size = round(len(cards_list) / num_epidemics)
        buckets = [cards_list[i:i+bucket_size] for i in range(0, len(cards_list), bucket_size)]
        buckets = [bucket+[EpidemicCard()] for bucket in buckets]
        for bucket in buckets: self.gen.shuffle(bucket)
        self.player_deck = deque([card for bucket in buckets for card in bucket])
        # Start the game.
        self.main_loop()

    def draw_infection_card(self, infections=1):
        target_city = self.infection_deck.pop()
        robo.do(target_city.name + " infection card", "infection deck", "infection discard")
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
        robo.do(card.name + " player card", "player deck", player.name + " hand")
        player.cards.append(card)

    def epidemic(self):
        self.infection_counter += 1 #Increase
        target_city = self.infection_deck.popleft() #Infect
        target_city.endemic_disease.infect(target_city, 3)
        self.infection_discard.append(target_city)
        self.gen.shuffle(self.infection_discard) #Intensify
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
            except (ValueError, IndexError) as e:
                print('Must be specified as one of the listed numbers.')
        return picked

    def player_turn(self, player): #Quick text-based interface for player turns.
        print(f'\n{player.name}\'s turn.')
        player.begin_turn()
        player.action_count = self.config['actions_per_turn']
        while player.action_count:
            print('You are', player.describe())
            action = self.pick('an action', player.actions)
            choices = action.choices(player, cards=player.cards, **self.__dict__) #Actions pretty much happen on a world-level and can view the full world state in order to decide what actions are legal and what isn't.
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
            action.execute(player, cards=player.cards, **chosen)
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
            active_player = self.players[0]
            self.player_turn(active_player)
            for i in range(self.config['city_cards_per_turn']):
                self.draw_player_card(active_player)
            self.check_discard(active_player)
            for i in range(self.config['infection_cards_per_turn'][self.infection_counter]):
                self.draw_infection_card()
            self.players.popleft()
            self.players.append(active_player)

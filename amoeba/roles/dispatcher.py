from amoeba.core import Player
from amoeba.abilities import *

class Convene(Ability):
    name = 'Convene'
    def choices(_, players, cities, **kwargs):
        chosen = yield 'player', players
        chosen = yield 'destination', [player.city for player in players if player != chosen['player']]
    def execute(_, player, cards, destination):
        player.goto(destination)

class Dispatch(Ability):
    name = 'Dispatch'
    def choices(dispatcher, cards, players, **kwargs):
        chosen = yield 'player', [player for player in players if player != dispatcher]
        chosen = yield 'action', [Drive, DirectFlight, CharterFlight, ShuttleFlight]
        additional_choices = chosen['action'].choices(chosen['player'], cards=cards, **kwargs)
        choice = next(additional_choices)
        while choice:
            chosen = yield choice[0], choice[1]
            try: choice = additional_choices.send(chosen)
            except StopIteration: break #Unsure why this doesn't just work its way up the call stack until it gets handled by the world level try/except StopIteration, but apparently it is needs to be handled here as well.
    def execute(dispatcher, cards, player, action, **kwargs):
        action.execute(player, cards, **kwargs)

class Dispatcher(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = [Drive, ShuttleFlight, DirectFlight, CharterFlight, Convene, Dispatch, TreatDisease, BuildResearch, ShareKnowledge, DiscoverCure, Ability]
        self.role_name = 'Dispatcher'

from amoeba.abilities import *

class PlayerCard:
    def __init__(self, type, name):
        self.type = type
        self.name = name

class CityCard(PlayerCard):
    def __init__(self, city):
        super().__init__('city', city.name)
        self.city = city
    def __eq__(self, other):
        return (self.city == other)

class EpidemicCard(PlayerCard):
    def __init__(self):
        super().__init__('epidemic', 'Epidemic')

class EventCard(PlayerCard):
    def __init__(self, ability):
        super().__init__('event', ability.name)
        self.ability = ability
        self.reclaimed = False

class Airlift(Ability):
    name = 'Airlift'
    def choices(player, cities, **kwargs):
        yield 'destination',  [city for city in cities if city != player.city]
    def execute(player, cards, destination):
        player.move(destination)

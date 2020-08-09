import amoeba.robo as robo

class Ability:
    name = 'Pass'
    def choices(player, **kwargs):
        yield
    def execute(player):
        return

class Drive(Ability):
    name = 'Drive'
    def choices(player, **kwargs):
        yield 'destination', player.city.neighbors
    def execute(player, destination):
        robo.do(player.name, player.city.name, destination.name)

class ShuttleFlight(Ability):
    name = 'Shuttle Flight'
    def choices(player, cities, **kwargs):
        if not player.city.research: yield 'destination', []
        yield 'destination', [city for city in cities.values() if (city.research and city != player.city)]
    def execute(player, destination):
        robo.do(player.name, player.city.name, destination.name)

class DirectFlight(Ability):
    name = 'Direct Flight'
    def choices(player, **kwargs):
        yield 'destination', [card.city for card in player.cards if (card.type == 'city' and card.city != player.city)]
    def execute(player, destination):
        player.cards.remove(destination)
        robo.do(player.name, player.city.name, destination.name)

class CharterFlight(Ability):
    name = 'Charter Flight'
    def choices(player, cities, **kwargs):
        if not any([card.city==player.city for card in player.cards]): yield 'destination', []
        yield 'destination', [city for city in cities.values() if city != player.city]
    def execute(player, destination):
        player.cards.remove(player.city)
        robo.do(player.name, player.city.name, destination.name)

class TreatDisease(Ability):
    name = 'Treat Disease'
    def choices(player, **kwargs):
        yield 'disease', [disease for disease in player.city.infections.keys() if player.city.infections[disease] != 0]
    def execute(player, disease):
        if disease.cured: disease.remove(player.city,3)
        else: disease.remove(player.city,1)

class BuildResearch(Ability):
    name = 'Build Research Station'
    def choices(player, **kwargs):
        if not any([card.city==player.city for card in player.cards]): yield 'location', []
        yield 'location', [player.city]
    def execute(player, location):
        player.cards.remove(location)
        location.reserch = True

class ShareKnowledge(Ability):
    name = 'Share Knowledge'
    def choices(player, players, **kwargs):
        chosen = yield 'teammate', [teammate for teammate in players if (teammate.city == player.city and teammate != player)]
        chosen = yield 'card', [card for card in player.cards if (card.type == 'city' and card.city == player.city)]+[card for card in chosen['teammate'].cards if (card.type == 'city' and card.city == player.city)]
    def execute(player, teammate, card):
        if card in player.cards:
            player.cards.remove(card)
            teammate.cards.append(card)
        else:
            teammate.cards.remove(card)
            player.cards.append(card)

class DiscoverCure(Ability):
    name = 'Discover Cure'
    def choices(player, diseases, **kwargs):
        chosen = yield 'disease', [disease for disease in diseases.values() if (not disease.cured and len([card for card in player.cards if card.city.endemic_disease == disease])>=5)]
        for i in range(1,6): chosen = yield f'card {i}', [card for card in player.cards if (card.city.endemic_disease == disease and card not in chosen.values())]
    def execute(player, **kwargs):
        for i in range(1,6): player.cards.remove(kwargs[f'card {i}'])
        kwargs['disease'].cured = True

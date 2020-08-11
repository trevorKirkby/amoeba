import amoeba.robo as robo

class Ability:
    name = 'Pass'
    def choices(player, **kwargs):
        yield
    def execute(player, cards):
        return

class Drive(Ability):
    name = 'Drive'
    def choices(player, **kwargs):
        yield 'destination', player.city.neighbors
    def execute(player, cards, destination):
        player.goto(destination)

class ShuttleFlight(Ability):
    name = 'Shuttle Flight'
    def choices(player, cities, **kwargs):
        if not player.city.research: yield 'destination', []
        yield 'destination', [city for city in cities.values() if (city.research and city != player.city)]
    def execute(player, cards, destination):
        player.goto(destination)

class DirectFlight(Ability):
    name = 'Direct Flight'
    def choices(player, cards, **kwargs):
        yield 'destination', [card.city for card in cards if (card.type == 'city' and card.city != player.city)]
    def execute(player, cards, destination):
        cards.remove(destination)
        player.goto(destination)

class CharterFlight(Ability):
    name = 'Charter Flight'
    def choices(player, cards, cities, **kwargs):
        if not any([card.city==player.city for card in cards]): yield 'destination', []
        yield 'destination', [city for city in cities.values() if city != player.city]
    def execute(player, cards, destination):
        cards.remove(player.city)
        player.goto(destination)

class TreatDisease(Ability):
    name = 'Treat Disease'
    def choices(player, **kwargs):
        yield 'disease', [disease for disease in player.city.infections.keys() if player.city.infections[disease] != 0]
    def execute(player, cards, disease):
        if disease.cured: disease.remove(player.city,3)
        else: disease.remove(player.city,1)

class BuildResearch(Ability):
    name = 'Build Research Station'
    def choices(player, cards, **kwargs):
        if not any([card.city==player.city for card in cards]): yield 'location', []
        yield 'location', [player.city]
    def execute(player, cards, location):
        cards.remove(location)
        location.reserch = True

class ShareKnowledge(Ability):
    name = 'Share Knowledge'
    def choices(player, cards, players, **kwargs):
        chosen = yield 'teammate', [teammate for teammate in players if (teammate.city == player.city and teammate != player)]
        chosen = yield 'card', [card for card in cards if (card.type == 'city' and card.city == player.city)]+[card for card in chosen['teammate'].cards if (card.type == 'city' and card.city == player.city)]
    def execute(player, cards, teammate, card):
        if card in cards:
            cards.remove(card)
            teammate.cards.append(card)
        else:
            teammate.cards.remove(card)
            cards.append(card)

class DiscoverCure(Ability):
    name = 'Discover Cure'
    def choices(player, cards, diseases, **kwargs):
        chosen = yield 'disease', [disease for disease in diseases.values() if (not disease.cured and len([card for card in cards if card.city.endemic_disease == disease])>=5)]
        for i in range(1,6): chosen = yield f'card {i}', [card for card in cards if (card.city.endemic_disease == disease and card not in chosen.values())]
    def execute(player, cards, **kwargs):
        for i in range(1,6): cards.remove(kwargs[f'card {i}'])
        kwargs['disease'].cured = True

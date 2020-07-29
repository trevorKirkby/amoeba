class Ability:
    name = ''
    def choices(self, player, **kwargs):
        yield
    def execute(self, player, **kwargs):
        return

class Drive(Ability):
    name = 'Drive'
    def choices(self, player, **kwargs):
        yield 'destination', player.city.edges
    def execute(self, player, **kwargs):
        player.move(kwargs['destination'])

class ShuttleFlight(Ability):
    name = 'Shuttle Flight'
    def choices(self, player, **kwargs):
        if not player.city.research: yield 'destination', []
        yield 'destination', [city for city in kwargs['cities'].values() if (city.research and city != player.city)]
    def execute(self, player, **kwargs):
        player.move(kwargs['destination'])

class DirectFlight(Ability):
    name = 'Direct Flight'
    def choices(self, player, **kwargs):
        yield 'destination', [card.city for card in player.cards if (card.type == 'city' and card.city != player.city)]
    def execute(self, player, **kwargs):
        player.cards.remove(kwargs['destination'])
        player.move(kwargs['destination'])

class CharterFlight(Ability):
    name = 'Charter Flight'
    def choices(self, player, **kwargs):
        if not any([card.city==player.city for card in player.cards]): yield 'destination', []
        yield 'destination', [city for city in kwargs['cities'].values() if city != player.city]
    def execute(self, player, **kwargs):
        player.cards.remove(kwargs['destination'])
        player.move(kwargs['destination'])

class TreatDisease(Ability):
    name = 'Treat Disease'
    def choices(self, player, **kwargs):
        yield 'disease', [disease for disease in player.city.infections.keys() if city.infections[disease] != 0]
    def execute(self, player, **kwargs):
        if kwargs['disease'].cured: kwargs['disease'].remove(player.city,3)
        else: kwargs['disease'].remove(player.city,1)

class BuildResearch(Ability):
    name = 'Build Research Station'
    def choices(self, player, **kwargs):
        if not any([card.city==player.city for card in player.cards]): yield 'location', []
        yield 'location', [player.city]
    def execute(self, player, **kwargs):
        player.cards.remove(kwargs['location'])
        kwargs['location'].reserch = True

class ShareKnowledge(Ability):
    name = 'Share Knowledge'
    def choices(self, player, **kwargs):
        yield 'teammate', [teammate for teammate in kwargs['players'] if (teammate.city == player.city and teammate != player)]
        chosen = yield 'card', [card for card in player.cards if card.type == 'city']+[card for card in chosen['teammate'].cards if card.type == 'city']
    def execute(self, player, **kwargs):
        if kwargs['card'] in player.cards:
            player.cards.remove(kwargs['card'])
            kwargs['teammate'].cards.append(kwargs['card'])
        else:
            kwargs['teammate'].cards.remove(kwargs['card'])
            player.cards.append(kwargs['card'])

class DiscoverCure(Ability):
    name = 'Discover Cure'
    def choices(self, player, **kwargs):
        yield 'disease', [disease for disease in kwargs['diseases'].values() if (not disease.cured and len([card for card in self.cards if card.city.endemic_disease == disease])>=5)]
        for i in range(1,6): chosen = yield f'card {i}', [card for card in self.cards if (card.city.endemic_disease == disease and card not in chosen.values())]
    def execute(self, player, **kwargs):
        for i in range(1,6): player.cards.remove(kwargs[f'card {i}'])
        kwargs['disease'].cured = True


import random



class games():

    def fnn_randcard(self,exclude_cards):
        'Picks a random card from a deck, excluding those given to it in a list'
        deck = [y + str(x).replace('11','j').replace('12','q').replace('13','k') for y in ['s','c','d','h'] for x in range(1,14)]
        for card in exclude_cards:
            deck.remove(card)
        num_cards = len(deck)
        rand_card = random.randint(0,num_cards)
        return deck[rand_card]

    def fn_random_card(self,args,client,destination):
        'Picks a random card from a deck.'
        card = games.fnn_randcard(self,[])
        carddesc = card[1:].replace('k','King').replace('q','Queen').replace('j','Jack') + " of "
        if(card[0]=='c'):
            carddesc = carddesc + "clubs"
        elif(card[0]=='s'):
            carddesc = carddesc + "spades"
        elif(card[0]=='d'):
            carddesc = carddesc + "diamonds"
        else:
            carddesc = carddesc + "hearts"
        return "I have chosen the " + carddesc + "."


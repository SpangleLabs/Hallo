
import random
import time
import datetime



class games():

    def fnn_randcard(self,exclude_cards):
        'Picks a random card from a deck, excluding those given to it in a list'
        deck = [y + str(x).replace('11','j').replace('12','q').replace('13','k') for y in ['s','c','d','h'] for x in range(1,14)]
        for card in exclude_cards:
            deck.remove(card)
        num_cards = len(deck)
        rand_card = random.randint(0,num_cards)
        return deck[rand_card]

    def fnn_cardname(self,card):
        carddesc = card[1:].replace('k','King').replace('q','Queen').replace('j','Jack') + " of "
        if(card[1:]=='1'):
            carddesc = "Ace of "
        if(card[0]=='c'):
            carddesc = carddesc + "clubs"
        elif(card[0]=='s'):
            carddesc = carddesc + "spades"
        elif(card[0]=='d'):
            carddesc = carddesc + "diamonds"
        else:
            carddesc = carddesc + "hearts"
        return carddesc

    def fnn_ordinal(self,number):
        if(number%10==1 and number%100!=11):
            return str(number) + "st"
        elif(number%10==2 and number%100!=12):
            return str(number) + "nd"
        elif(number%10==3 and number%100!=13):
            return str(number) + "rd"
        else:
            return str(number) + "th"

    def fnn_date(self,timestamp):
        datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def fn_random_card(self,args,client,destination):
        'Picks a random card from a deck.'
        card = games.fnn_randcard(self,[])
        carddesc = games.fnn_cardname(self,card)
        return "I have chosen the " + carddesc + "."

    def fn_higher_or_lower(self,args,client,destination):
        'play a game of higher or lower. Syntax: "higher_or_lower start" to start a game, "higher_or_lower higher" to guess the next card will be higher, "higher_or_lower lower" to guess the next card will be lower, "higher_or_lower end" to quit the game.'
        try:
            self.games
        except:
            self.games = {}
        if('server' not in self.games):
            self.games['server'] = {}
        if(destination[0] not in self.games['server']):
            self.games['server'][destination[0]] = {}
            self.games['server'][destination[0]]['player'] = {}
        if(args.lower()=='start'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                return "You're already playing a game."
            else:
                if(client not in self.games['server'][destination[0]]['player']):
                    self.games['server'][destination[0]]['player'][client] = {}
                self.games['server'][destination[0]]['player'][client]['higher_or_lower'] = {}
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['start_time'] = time.time()
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_time'] = time.time()
                first_card = games.fnn_randcard(self,[])
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = first_card
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'] = [first_card]
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] = 1
                return "You have started a game of higher or lower. Your first card is: " + games.fnn_cardname(self,first_card)
        elif(args.lower()=='lower'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                next_card = games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'])
                cardnum = int(next_card[1:].replace('j','11').replace('q','12').replace('k','13'))
                last_cardnum = int(self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'][1:].replace('j','11').replace('q','12').replace('k','13'))
                if(cardnum<last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + games.fnn_ordinal(self,turns) + " card is " + games.fnn_cardname(self,next_card) + ", which is lower! Congrats! Do you think the next card will be higher or lower?"
                elif(cardnum==last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + games.fnn_ordinal(self,turns) + " card is " + games.fnn_cardname(self,next_card) + ", which is the same (that's fine.) Do you think the next card will be higher or lower?"
                else:
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    del self.games['server'][destination[0]]['player'][client]['higher_or_lower']
                    if('highscores' not in self.conf):
                        self.conf['highscores'] = {}
                    if('higher_or_lower' not in self.conf['highscores']):
                        self.conf['highscores']['higher_or_lower'] = {}
                    if('score' not in self.conf['highscores']['higher_or_lower'] or turns>self.conf['highscores']['higher_or_lower']['score']):
                        if('score' in self.conf['highscores']['higher_or_lower']):
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['client'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['score'] = turns
                        self.conf['highscores']['higher_or_lower']['name'] = client
                        self.conf['highscores']['higher_or_lower']['date'] = time.time()
                        return "Your " + games.fnn_ordinal(self,turns+1) + " card is " + games.fnn_cardname(self,next_card) + ". Sorry, that's higher, you lose. You managed " + str(turns) + " cards though, that's a new highscore!" + previous_score
                    else:
                        return "Your " + games.fnn_ordinal(self,turns+1) + " card is " + games.fnn_cardname(self,next_card) + ". Sorry, that's higher, you lose. You managed " + str(turns) + " cards though."
            else:
                return "You're not currently playing a game, use 'higher_or_lower start' to start a game."
        elif(args.lower()=='higher'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                next_card = games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'])
                cardnum = int(next_card[1:].replace('j','11').replace('q','12').replace('k','13'))
                last_cardnum = int(self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'][1:].replace('j','11').replace('q','12').replace('k','13'))
                if(cardnum>last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + games.fnn_ordinal(self,turns) + " card is " + games.fnn_cardname(self,next_card) + ", which is higher! Congrats! Do you think the next card will be higher or lower?"
                elif(cardnum==last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + games.fnn_ordinal(self,turns) + " card is " + games.fnn_cardname(self,next_card) + ", which is the same (that's fine.) Do you think the next card will be higher or lower?"
                else:
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    del self.games['server'][destination[0]]['player'][client]['higher_or_lower']
                    if('highscores' not in self.conf):
                        self.conf['highscores'] = {}
                    if('higher_or_lower' not in self.conf['highscores']):
                        self.conf['highscores']['higher_or_lower'] = {}
                    if('score' not in self.conf['highscores']['higher_or_lower'] or turns>self.conf['highscores']['higher_or_lower']['score']):
                        if('score' in self.conf['highscores']['higher_or_lower']):
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['client'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['score'] = turns
                        self.conf['highscores']['higher_or_lower']['name'] = client
                        self.conf['highscores']['higher_or_lower']['date'] = time.time()
                        return "Your " + games.fnn_ordinal(self,turns+1) + " card is " + games.fnn_cardname(self,next_card) + ". Sorry, that's lower, you lose. You managed " + str(turns) + " cards though, that's a new highscore!" + previous_score
                    else:
                        return "Your " + games.fnn_ordinal(self,turns+1) + " card is " + games.fnn_cardname(self,next_card) + ". Sorry, that's lower, you lose. You managed " + str(turns) + " cards though."
            else:
                return "You're not currently playing a game, use 'higher_or_lower start' to start a game."
        elif(args.lower()=='end'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                del self.games['server'][destination[0]]['player'][client]['higher_or_lower']
                if('highscores' not in self.conf):
                    self.conf['highscores'] = {}
                if('higher_or_lower' not in self.conf['highscores']):
                    self.conf['highscores']['higher_or_lower'] = {}
                if('score' not in self.conf['highscores']['higher_or_lower'] or turns>self.conf['highscores']['higher_or_lower']['score']):
                    if('score' in self.conf['highscores']['higher_or_lower']):
                        previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['client'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                    else:
                        previous_score = ""
                    self.conf['highscores']['higher_or_lower']['score'] = turns
                    self.conf['highscores']['higher_or_lower']['name'] = client
                    self.conf['highscores']['higher_or_lower']['date'] = time.time()
                    return "Sorry to see you quit, you had managed " + str(turns) + " cards, which is a new highscore!" + previous_score
                else:
                    return "Sorry to see you quit, you had managed " + str(turns) + " cards."
        else:
            return "I don't understand this input." + ' Syntax: "higher_or_lower start" to start a game, "higher_or_lower higher" to guess the next card will be higher, "higher_or_lower lower" to guess the next card will be lower, "higher_or_lower end" to quit the game.'









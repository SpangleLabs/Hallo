
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
        rand_card = random.randint(0,num_cards-1)
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
        return str(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

    def fnn_cardsum(self,cards):
        sum = 0
        for card in cards:
            cardvalue = int(card[1:].replace('j','10').replace('q','10').replace('k','10'))
            sum = sum + cardvalue
        return sum

    def fnn_cardsinhand(self,hand,check):
        cards = []
        if(check in ['c','d','s','h']):
            for card in hand:
                if(card[0]==check):
                    cards.append(card)
        elif(check in ['1','2','3','4','5','6','7','8','9','10','j','q','k']):
            for card in hand:
                if(card[1:]==check):
                    cards.append(card)
        else:
            for card in hand:
                if(card==check):
                    cards.append(card)
        return cards

    def fn_date(self,args,client,destination):
        'returns datestamp from unix time'
        try:
            args = int(args)
        except:
            return "Invalid timestamp"
        return games.fnn_date(self,args)

    def fn_random_card(self,args,client,destination):
        'Picks a random card from a deck.'
        card = games.fnn_randcard(self,[])
        carddesc = games.fnn_cardname(self,card)
        return "I have chosen the " + carddesc + "."

    def fn_highscores(self,args,client,destination):
        'view the highscores for all games.'
        output = "Highscores:\n"
        if('highscores' not in self.conf):
            self.conf['highscores'] = {}
        for game in self.conf['highscores']:
            game_name = game
            if('game_name' in self.conf['highscores'][game]):
                game_name = self.conf['highscores'][game]['game_name']
            output = output + game_name + "> Score: " + str(self.conf['highscores'][game]['score']) + ", Player: " + self.conf['highscores'][game]['name'] + ", Date: " + games.fnn_date(self,self.conf['highscores'][game]['date']) + "\n"
        return output

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
        if(args.lower()=='start' or args==''):
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
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['game_name'] = 'Higher or lower'
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
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['game_name'] = 'Higher or lower'
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
                        previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ")"
                    else:
                        previous_score = ""
                    self.conf['highscores']['higher_or_lower']['game_name'] = 'Higher or lower'
                    self.conf['highscores']['higher_or_lower']['score'] = turns
                    self.conf['highscores']['higher_or_lower']['name'] = client
                    self.conf['highscores']['higher_or_lower']['date'] = time.time()
                    return "Sorry to see you quit, you had managed " + str(turns) + " cards, which is a new highscore!" + previous_score
                else:
                    return "Sorry to see you quit, you had managed " + str(turns) + " cards."
        else:
            return "I don't understand this input." + ' Syntax: "higher_or_lower start" to start a game, "higher_or_lower higher" to guess the next card will be higher, "higher_or_lower lower" to guess the next card will be lower, "higher_or_lower end" to quit the game.'





    def fn_blackjack(self,args,client,destination):
        "A game of blackjack against hallo. Syntax: 'blackjack start' to start a game, 'blackjack hit' to hit, 'blackjack stick' or 'blackjack stand' to stick/stand."
        try:
            self.games
        except:
            self.games = {}
        if('server' not in self.games):
            self.games['server'] = {}
        if(destination[0] not in self.games['server']):
            self.games['server'][destination[0]] = {}
            self.games['server'][destination[0]]['player'] = {}
        if(args.lower()=='start' or args.lower()==''):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                return "You're already playing a game."
            else:
                if(client not in self.games['server'][destination[0]]['player']):
                    self.games['server'][destination[0]]['player'][client] = {}
                self.games['server'][destination[0]]['player'][client]['blackjack'] = {}
                self.games['server'][destination[0]]['player'][client]['blackjack']['start_time'] = time.time()
                self.games['server'][destination[0]]['player'][client]['blackjack']['last_time'] = time.time()
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'] = []
                first_card = games.fnn_randcard(self,[])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(first_card)
                second_card = games.fnn_randcard(self,[first_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] = [second_card]
                third_card = games.fnn_randcard(self,[first_card,second_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(third_card)
                forth_card = games.fnn_randcard(self,[first_card,second_card,third_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'] = []
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'].append(forth_card)
                if((first_card[1:]=='1' and third_card[1:] in ['10','j','q','k']) or (third_card[1:]=='1' and first_card[1:] in ['10','j','q','k'])):
                    return "You have started a game of Blackjack (H17), you have been dealt a " + games.fnn_cardname(self,first_card) + " and a " + games.fnn_cardname(self,third_carD) + ". Congratulations! That's a blackjack! You win."
                #insert a check for a blackjack here.
                return "You have started a game of Blackjack (H17), you have been dealt a " + games.fnn_cardname(self,first_card) + " and a " + games.fnn_cardname(self,third_card) + ". The dealer has a " + games.fnn_cardname(self,second_card) + " and another, covered, card. Would you like to hit or stick?"
        elif(args.lower()=='hit'):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                new_card = games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(new_card)
                card_sum = games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'])
                if(card_sum>21):
                    del self.games['server'][destination[0]]['player'][client]['blackjack']
                    return "You have been dealt a " + games.fnn_cardname(self,new_card) + ", which means your hand sums to " + str(card_sum) + ". You've gone bust. You lose, sorry."
                else:
                    return "You have been dealt a " + games.fnn_cardname(self,new_card) + ", would you like to hit or stick?"
            else:
                return "You're not even playing a game of blackjack, use 'blackjack start' to start playing one."
        elif(args.lower()=='stick' or args.lower()=='stand'):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                #game is over, deal to finish dealer's hand, sum up both player and dealer hands, see who wins.
                player_sum = games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'])
                player_aces = len(games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'],'1'))
                if(player_aces>0 and player_sum<=11):
                    player_sum = player_sum + 10
                output = "Your hand is: " + ', '.join([games.fnn_cardname(self,card) for card in self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand']]) + ". Which sums to: " + str(player_sum) + ".\n"
                dealer_sum = games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']) 
                dealer_aces = len(games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'],'1'))
                if(dealer_aces>0 and dealer_sum<=11):
                    dealer_sum = dealer_sum + 10
                dealer_newcards = 0
                while(dealer_sum<17 or (dealer_sum==17 and dealer_aces>0)):
                    dealer_newcards += 1
                    dealer_newcard = games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'])
                    self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'].append(dealer_newcard)
                    dealer_sum = games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']) 
                    dealer_aces = len(games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'],'1'))
                    if(dealer_aces>0 and dealer_sum<=11):
                        dealer_sum = dealer_sum + 10
                if(dealer_newcards!=0):
                    plural = 'card'
                    if(dealer_newcards!=1):
                        plural = 'cards'
                    output = output + "The dealer deals himself " + str(dealer_newcards) + " more " + plural + ".\n"
                output = output + "The dealer's hand is: " + ', '.join([games.fnn_cardname(self,card) for card in self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']]) + ". Which sums to: " + str(dealer_sum) + "\n"
                if(dealer_sum==player_sum):
                    output = output + "It's a tie."
                elif(dealer_sum>player_sum):
                    output = output + "Dealer wins."
                else:
                    output = output + "You win! Congratulations!"
                del self.games['server'][destination[0]]['player'][client]['blackjack']
                return output
            else:
                return "You're not even playing a game of blackjack, use 'blackjack start' to start playing one."
        elif(args.lower()=='end'):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                player_sum = 0
                dealer_sum = 0
                del self.games['server'][destination[0]]['player'][client]['blackjack']
                return "You have quit the game. You had " + str(player_sum) + " and the dealer had " + str(dealer_sum) + "."
            else:
                return "You're not even playing a game of blackjack, use 'blackjack start' to start playing one."
        else:
            return "I don't understand this input." + ' Syntax: "blackjack start" to start a game, "blackjack hit" to hit, "blackjack stick" to stick, and "blackjack end" to quit the game.'






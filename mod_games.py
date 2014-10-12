import random
import time
import datetime
import pprint
import hashlib
import os

import ircbot_chk

class mod_games():

    def fn_games_clear(self,args,client,destination):
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "This function is for gods only."
        del self.games
        return "Deleted all games."
    
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
        card_sum = 0
        for card in cards:
            cardvalue = int(card[1:].replace('j','10').replace('q','10').replace('k','10'))
            card_sum = card_sum + cardvalue
        return card_sum

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
        'Returns the date from a given unix timestamp. Format: date <timestamp>'
        try:
            args = int(args)
        except:
            return "Invalid timestamp"
        return mod_games.fnn_date(self,args) + "."

    def fn_random_card(self,args,client,destination):
        'Picks a random card from a deck. Format: random_card'
        card = mod_games.fnn_randcard(self,[])
        carddesc = mod_games.fnn_cardname(self,card)
        return "I have chosen the " + carddesc + "."

    def fn_highscores(self,args,client,destination):
        'View the highscores for all games. Format: highscores'
        output = "Highscores:\n"
        if('highscores' not in self.conf):
            self.conf['highscores'] = {}
        for game in self.conf['highscores']:
            game_name = game
            if('game_name' in self.conf['highscores'][game]):
                game_name = self.conf['highscores'][game]['game_name']
            output = output + game_name + "> Score: " + str(self.conf['highscores'][game]['score']) + ", Player: " + self.conf['highscores'][game]['name'] + ", Date: " + mod_games.fnn_date(self,self.conf['highscores'][game]['date']) + ".\n"
        return output

    def fn_games_view(self,args,client,destination):
        'View the games variable, privmsg only. gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole core variable here, that would be rude."
            else:
#                return "erm, really? my core variable... erm, if you insist. Here goes:\n" + pprint.pformat(self.core)
                prettycore = pprint.pformat(self.games)
                filename = "core_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode('utf-8')).hexdigest() + ".txt"
                link = "http://sucs.org/~drspangle/" + filename
                file = open("../public_html/" + filename,'w')
                file.write(prettycore)
                file.close()
                self.base_say("Core written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../public_html/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view core variable."
        
    def fn_higher_or_lower(self,args,client,destination):
        'Play a game of higher or lower. Format: "higher_or_lower start" to start a game, "higher_or_lower higher" to guess the next card will be higher, "higher_or_lower lower" to guess the next card will be lower, "higher_or_lower end" to quit the game.'
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
                first_card = mod_games.fnn_randcard(self,[])
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = first_card
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'] = [first_card]
                self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] = 1
                return "You have started a game of higher or lower. Your first card is: " + mod_games.fnn_cardname(self,first_card) + "."
        elif(args.lower()=='lower'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                next_card = mod_games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'])
                cardnum = int(next_card[1:].replace('j','11').replace('q','12').replace('k','13'))
                last_cardnum = int(self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'][1:].replace('j','11').replace('q','12').replace('k','13'))
                if(cardnum<last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + mod_games.fnn_ordinal(self,turns) + " card is " + mod_games.fnn_cardname(self,next_card) + ", which is lower! Congrats! Do you think the next card will be higher or lower?"
                elif(cardnum==last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + mod_games.fnn_ordinal(self,turns) + " card is " + mod_games.fnn_cardname(self,next_card) + ", which is the same (that's fine.) Do you think the next card will be higher or lower?"
                else:
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    del self.games['server'][destination[0]]['player'][client]['higher_or_lower']
                    if('highscores' not in self.conf):
                        self.conf['highscores'] = {}
                    if('higher_or_lower' not in self.conf['highscores']):
                        self.conf['highscores']['higher_or_lower'] = {}
                    if('score' not in self.conf['highscores']['higher_or_lower'] or turns>self.conf['highscores']['higher_or_lower']['score']):
                        if('score' in self.conf['highscores']['higher_or_lower']):
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + mod_games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ".)"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['game_name'] = 'Higher or lower'
                        self.conf['highscores']['higher_or_lower']['score'] = turns
                        self.conf['highscores']['higher_or_lower']['name'] = client
                        self.conf['highscores']['higher_or_lower']['date'] = time.time()
                        return "Your " + mod_games.fnn_ordinal(self,turns+1) + " card is " + mod_games.fnn_cardname(self,next_card) + ". Sorry, that's higher, you lose. You managed " + str(turns) + " cards though, that's a new highscore!" + previous_score
                    else:
                        return "Your " + mod_games.fnn_ordinal(self,turns+1) + " card is " + mod_games.fnn_cardname(self,next_card) + ". Sorry, that's higher, you lose. You managed " + str(turns) + " cards though."
            else:
                return "You're not currently playing a game, use 'higher_or_lower start' to start a game."
        elif(args.lower()=='higher'):
            if(client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                next_card = mod_games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'])
                cardnum = int(next_card[1:].replace('j','11').replace('q','12').replace('k','13'))
                last_cardnum = int(self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'][1:].replace('j','11').replace('q','12').replace('k','13'))
                if(cardnum>last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + mod_games.fnn_ordinal(self,turns) + " card is " + mod_games.fnn_cardname(self,next_card) + ", which is higher! Congrats! Do you think the next card will be higher or lower?"
                elif(cardnum==last_cardnum):
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['last_card'] = next_card
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['cards'].append(next_card)
                    self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns'] += 1
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    return "Your " + mod_games.fnn_ordinal(self,turns) + " card is " + mod_games.fnn_cardname(self,next_card) + ", which is the same (that's fine.) Do you think the next card will be higher or lower?"
                else:
                    turns = self.games['server'][destination[0]]['player'][client]['higher_or_lower']['turns']
                    del self.games['server'][destination[0]]['player'][client]['higher_or_lower']
                    if('highscores' not in self.conf):
                        self.conf['highscores'] = {}
                    if('higher_or_lower' not in self.conf['highscores']):
                        self.conf['highscores']['higher_or_lower'] = {}
                    if('score' not in self.conf['highscores']['higher_or_lower'] or turns>self.conf['highscores']['higher_or_lower']['score']):
                        if('score' in self.conf['highscores']['higher_or_lower']):
                            previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + mod_games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ".)"
                        else:
                            previous_score = ""
                        self.conf['highscores']['higher_or_lower']['game_name'] = 'Higher or lower'
                        self.conf['highscores']['higher_or_lower']['score'] = turns
                        self.conf['highscores']['higher_or_lower']['name'] = client
                        self.conf['highscores']['higher_or_lower']['date'] = time.time()
                        return "Your " + mod_games.fnn_ordinal(self,turns+1) + " card is " + mod_games.fnn_cardname(self,next_card) + ". Sorry, that's lower, you lose. You managed " + str(turns) + " cards though, that's a new highscore!" + previous_score
                    else:
                        return "Your " + mod_games.fnn_ordinal(self,turns+1) + " card is " + mod_games.fnn_cardname(self,next_card) + ". Sorry, that's lower, you lose. You managed " + str(turns) + " cards though."
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
                        previous_score = " (previous highscore was: " + str(self.conf['highscores']['higher_or_lower']['score']) + " cards, set by " + self.conf['highscores']['higher_or_lower']['name'] + " " + mod_games.fnn_date(self,self.conf['highscores']['higher_or_lower']['date']) + ".)"
                    else:
                        previous_score = "."
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
        "A game of blackjack against hallo. Format: 'blackjack start' to start a game, 'blackjack hit' to hit, 'blackjack stick' or 'blackjack stand' to stick/stand."
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
                first_card = mod_games.fnn_randcard(self,[])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(first_card)
                second_card = mod_games.fnn_randcard(self,[first_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] = [second_card]
                third_card = mod_games.fnn_randcard(self,[first_card,second_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(third_card)
                forth_card = mod_games.fnn_randcard(self,[first_card,second_card,third_card])
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'] = []
                self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'].append(forth_card)
                if((first_card[1:]=='1' and third_card[1:] in ['10','j','q','k']) or (third_card[1:]=='1' and first_card[1:] in ['10','j','q','k'])):
                    del self.games['server'][destination[0]]['player'][client]['blackjack']
                    return "You have started a game of Blackjack (H17), you have been dealt a " + mod_games.fnn_cardname(self,first_card) + " and a " + mod_games.fnn_cardname(self,third_card) + ". Congratulations! That's a blackjack! You win."
                #insert a check for a blackjack here.
                return "You have started a game of Blackjack (H17), you have been dealt a " + mod_games.fnn_cardname(self,first_card) + " and a " + mod_games.fnn_cardname(self,third_card) + ". The dealer has a " + mod_games.fnn_cardname(self,second_card) + " and another, covered, card. Would you like to hit or stick?"
        elif(args.lower()=='hit'):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                new_card = mod_games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'])
                self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'].append(new_card)
                card_sum = mod_games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'])
                if(card_sum>21):
                    del self.games['server'][destination[0]]['player'][client]['blackjack']
                    return "You have been dealt a " + mod_games.fnn_cardname(self,new_card) + ", which means your hand sums to " + str(card_sum) + ". You've gone bust. You lose, sorry."
                else:
                    return "You have been dealt a " + mod_games.fnn_cardname(self,new_card) + ", would you like to hit or stick?"
            else:
                return "You're not even playing a game of blackjack, use 'blackjack start' to start playing one."
        elif(args.lower()=='stick' or args.lower()=='stand'):
            if(client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                #game is over, deal to finish dealer's hand, sum up both player and dealer hands, see who wins.
                player_sum = mod_games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'])
                player_aces = len(mod_games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'],'1'))
                if(player_aces>0 and player_sum<=11):
                    player_sum = player_sum + 10
                output = "Your hand is: " + ', '.join([mod_games.fnn_cardname(self,card) for card in self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand']]) + ". Which sums to: " + str(player_sum) + ".\n"
                dealer_sum = mod_games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']) 
                dealer_aces = len(mod_games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'],'1'))
                if(dealer_aces>0 and dealer_sum<=11):
                    dealer_sum = dealer_sum + 10
                dealer_newcards = 0
                while(dealer_sum<17 or (dealer_sum==17 and dealer_aces>0)):
                    dealer_newcards += 1
                    dealer_newcard = mod_games.fnn_randcard(self,self.games['server'][destination[0]]['player'][client]['blackjack']['player_hand'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'])
                    self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'].append(dealer_newcard)
                    dealer_sum = mod_games.fnn_cardsum(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']) 
                    dealer_aces = len(mod_games.fnn_cardsinhand(self,self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards'],'1'))
                    if(dealer_aces>0 and dealer_sum<=11):
                        dealer_sum = dealer_sum + 10
                if(dealer_newcards!=0):
                    plural = 'card'
                    if(dealer_newcards!=1):
                        plural = 'cards'
                    output = output + "The dealer deals himself " + str(dealer_newcards) + " more " + plural + ".\n"
                output = output + "The dealer's hand is: " + ', '.join([mod_games.fnn_cardname(self,card) for card in self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_upcard'] + self.games['server'][destination[0]]['player'][client]['blackjack']['dealer_downcards']]) + ". Which sums to: " + str(dealer_sum) + "\n"
                if(dealer_sum>21):
                    output = output + "Dealer busts.\n"
                if(dealer_sum==player_sum):
                    output = output + "It's a tie, and so the dealer wins."
                elif(dealer_sum>player_sum and dealer_sum<=21):
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

    def fnn_ddr_start(self,difficulty,destination):
        'Helper method, starts and runs a DDR game.'
        if(difficulty=="hard"):
            num_turns = 20
            time_min = 1
            time_max = 2
        elif(difficulty=="medium"):
            num_turns = 15
            time_min = 3
            time_max = 5
        else:
            num_turns = 10
            time_min = 5
            time_max = 8
        directions = ['^','v','>','<']
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr'] = {}
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'] = {}
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['num_turns'] = -1
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_direction'] = ''
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_time'] = 0
        self.base_say("Starting new game of DDR in 5 seconds, say 'join' to join.",destination)
        time.sleep(5)
        if(len(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])==0):
            self.base_say("0 players joined. Game over.",destination)
            return
        num_players = len(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])
        self.base_say(str(num_players)+" players joined: "+", ".join(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])+". Starting game.",destination)
        for turn in range(num_turns):
            direction = directions[random.randint(0,3)]
            self.base_say(direction,destination)
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['num_turns'] = turn
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_direction'] = direction
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_time'] = time.time()
            time.sleep(random.uniform(time_min,time_max))
        return
    
    def fnn_ddr_join(self,player,destination):
        'Processes a join request from a potential player.'
        try:
            self.games
        except:
            return
        if('server' not in self.games):
            return
        if(destination[0] not in self.games['server']):
            return
        if('channel' not in self.games['server'][destination[0]]):
            return
        if(destination[1] not in self.games['server'][destination[0]]['channel']):
            return
        if('ddr' not in self.games['server'][destination[0]]['channel'][destination[1]]):
            return
        if(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['num_turns']!=-1):
            return
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player] = {}
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits'] = 0
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag'] = 0
        self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['last_hit'] = 0
        return
    
    def fnn_ddr_move(self,player,move,destination):
        'Processes a potential move by a player.'
        move = move.lower().strip()
        move = move.replace('w','^').replace('a','<').replace('s','v').replace('d','>')
        print("1")
        try:
            self.games
        except:
            return
        print("2")
        if('server' not in self.games):
            return
        print("3")
        if(destination[0] not in self.games['server']):
            return
        print("4")
        if('channel' not in self.games['server'][destination[0]]):
            return
        print("5")
        if(destination[1] not in self.games['server'][destination[0]]['channel']):
            return
        print("6")
        if('ddr' not in self.games['server'][destination[0]]['channel'][destination[1]]):
            return
        print("7")
        if(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['num_turns']==-1):
            return
        print("8")
        if(player not in self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players']):
            return
        print("9")
        if(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['last_hit']>self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_time']):
            return
        print("a")
        if(move==self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_direction']):
            print("hit")
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits'] += 1
            lag = time.time()-self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['last_time']
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag'] = lag
            self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['last_hit'] = time.time()
        print("b")
        
    def fnn_ddr_end(self,destination):
        'Helper method, ends a DDR game.'
        if(len(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])==0):
            return
        self.base_say("Game has finished!",destination)
        winner = list(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])[0]
        if(len(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'])>=2):
            winner = mod_games.fnn_ddr_winner(self,self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'],destination)
            self.base_say("Winner is: "+winner,destination)
        total_turns = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['num_turns']+1
        for player in self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players']:
            hits = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits']
            lag = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag']
            self.base_say(player+" rating is: "+mod_games.fnn_ddr_rating(self,total_turns,hits,lag),destination)
        if('highscores' not in self.conf):
            self.conf['highscores'] = {}
        if('ddr' not in self.conf['highscores']):
            self.conf['highscores']['ddr'] = {}
        ######DOWN FROM HERE IS NOT DONE
        winner_hits = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][winner]['hits']
        winner_lag = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][winner]['lag']
        if('score' not in self.conf['highscores']['ddr']):
            mod_games.fnn_ddr_new_highscore(self,winner,winner_hits,winner_lag,destination)
            del self.games['server'][destination[0]]['channel'][destination[1]]['ddr']
            return
        if(winner_hits>self.conf['highscores']['ddr']['hits']):
            mod_games.fnn_ddr_new_highscore(self,winner,winner_hits,winner_lag,destination)
            del self.games['server'][destination[0]]['channel'][destination[1]]['ddr']
            return
        if(winner_hits==self.conf['highscores']['ddr']['hits'] and winner_lag<self.conf['highscores']['ddr']['lag']):
            mod_games.fnn_ddr_new_highscore(self,winner,winner_hits,winner_lag,destination)
            del self.games['server'][destination[0]]['channel'][destination[1]]['ddr']
            return
        del self.games['server'][destination[0]]['channel'][destination[1]]['ddr']
        return
        
    def fnn_ddr_new_highscore(self,player,hits,lag,destination):
        'Helper function, sets a new highscore for DDR'
        self.base_say(player+" has set a new DDR highscore with "+str(hits)+" hits and "+str(lag)+" lag!",destination)
        self.conf['highscores']['ddr']['score'] = str(hits)+" hits, "+str(lag)+"s lag"
        self.conf['highscores']['ddr']['hits'] = hits
        self.conf['highscores']['ddr']['lag'] = lag
        self.conf['highscores']['ddr']['name'] = player
        self.conf['highscores']['ddr']['date'] = time.time()
        
    def fnn_ddr_winner(self,players,destination):
        'Helper function, tells which player is winner from a set of players'
        winner = ''
        winner_hits = 0
        winner_lag = 0
        for player in players:
            if(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits']>winner_hits):
                winner = player
                winner_hits = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits']
                winner_lag = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag']
            elif(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits']==winner_hits):
                if(self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag']<winner_lag):
                    winner = player
                    winner_hits = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['hits']
                    winner_lag = self.games['server'][destination[0]]['channel'][destination[1]]['ddr']['players'][player]['lag']
        return winner

    def fnn_ddr_rating(self,turns,hits,lag):
        if(hits==turns):
            if(lag<5):
                return "Marvelous!!"
            else:
                return "Perfect!"
        elif(hits>=turns*0.75):
            return "Great"
        elif(hits>=turns*0.5):
            return "Good"
        elif(hits>=turns*0.25):
            return "Almost"
        else:
            return "Failure."
        
    def fn_ddr(self,args,client,destination):
        'Starts a new game of DDR. Format: ddr <difficulty>. Where difficulty is easy, medium or hard.'
        #check in a channel
        if(destination[1][0]!="#"):
            return "You must play DDR in a channel, not privmsg."
        #initialise games variable
        try:
            self.games
        except:
            self.games = {}
        if('server' not in self.games):
            self.games['server'] = {}
        if(destination[0] not in self.games['server']):
            self.games['server'][destination[0]] = {}
        if('channel' not in self.games['server'][destination[0]]):
            self.games['server'][destination[0]]['channel'] = {}
        if(destination[1] not in self.games['server'][destination[0]]['channel']):
            self.games['server'][destination[0]]['channel'][destination[1]] = {}
        #check no game is going
        if('ddr' in self.games['server'][destination[0]]['channel'][destination[1]]):
            return "A game is already in progress here."
        #check the given arguments
        args = args.lower().strip()
        if(args in ['','easy']):
            mod_games.fnn_ddr_start(self,"easy",destination)
        elif(args in ['medium','med']):
            mod_games.fnn_ddr_start(self,"medium",destination)
        elif(args in ['hard']):
            mod_games.fnn_ddr_start(self,"hard",destination)
        else:
            return "Invalid difficulty mode. Please specify easy, medium or hard."
        mod_games.fnn_ddr_end(self,destination)
        return
        


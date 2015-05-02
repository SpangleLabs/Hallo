

class Card:
    '''
    Card object, for use by higher or lower, blackjack, and any other card games.
    '''
    #Constants
    SUIT_DIAMONDS = "diamonds"
    SUIT_HEARTS = "hearts"
    SUIT_CLUBS = "clubs"
    SUIT_SPADES = "spades"
    COLOUR_RED = "red"
    COLOUR_BLACK = "black"
    CARD_ACE = 1
    CARD_2 = 2
    CARD_3 = 3
    CARD_4 = 4
    CARD_5 = 5
    CARD_6 = 6
    CARD_7 = 7
    CARD_8 = 8
    CARD_9 = 9
    CARD_10 = 10
    CARD_JACK = "jack"
    CARD_QUEEN = "queen"
    CARD_KING = "king"
    #Parameters
    mDeck = None
    mSuit = None
    mColour = None
    mValue = None

    def __init__(self,deck,suit,value):
        '''
        Constructor
        '''
        self.mDeck = deck
        if(suit in [self.SUIT_DIAMONDS,self.SUIT_HEARTS]):
            self.mSuit = suit
            self.mColour = self.COLOUR_RED
        elif(suit in [self.SUIT_CLUBS,self.SUIT_SPADES]):
            self.mSuit = suit
            self.mColour = self.COLOUR_BLACK
        else:
            raise Exception("Invalid suit")
        if(value in [self.CARD_ACE,self.CARD_2,self.CARD_3,self.CARD_4,self.CARD_5,self.CARD_6,self.CARD_7,self.CARD_8,self.CARD_9,self.CARD_10,self.CARD_JACK,self.CARD_QUEEN,self.CARD_KING]):
            self.mValue = value
        else:
            raise Exception("Invalid value")
    
    def __str__(self):
        return self.toString()
    
    def toString(self):
        'Outputs a string representing the card\'s value and suit.'
        if(self.mValue == self.CARD_ACE):
            cardValue = "Ace"
        elif(self.mValue == self.CARD_JACK):
            cardValue = "Jack"
        elif(self.mValue == self.CARD_QUEEN):
            cardValue = "Queen"
        elif(self.mValue == self.CARD_KING):
            cardValue = "King"
        else:
            cardValue = str(self.mValue)
        if(self.mSuit == self.SUIT_CLUBS):
            cardSuit = "clubs"
        elif(self.mSuit == self.SUIT_DIAMONDS):
            cardSuit = "diamonds"
        elif(self.mSuit == self.SUIT_HEARTS):
            cardSuit = "hearts"
        elif(self.mSuit == self.SUIT_SPADES):
            cardSuit = "spades"
        else:
            raise Exception("invalid suit")
        return cardValue + " of " + cardSuit
        
    def sumValue(self):
        'Outputs the value as an integer.'
        if(self.mValue in [self.CARD_JACK,self.CARD_QUEEN,self.CARD_KING]):
            return 10
        return int(self.mValue)


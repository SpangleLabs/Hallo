import random
from Function import Function

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
    mInDeck = True

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
    
    def isInDeck(self):
        'boolean, whether the card is still in the deck.'
        return self.mInDeck
    
    def setInDeck(self,inDeck):
        'mInDeck setter'
        self.mInDeck = inDeck
    
    def getSuit(self):
        'Suit getter'
        return self.mSuit
    
    def getColour(self):
        'Colour getter'
        return self.mColour
    
    def getValue(self):
        'Value getter'
        return self.mValue

class Deck:
    '''
    Deck object, for use by higher or lower, blackjack, and any other card games.
    Generates 52 cards and can then shuffle them.
    WILL NOT SHUFFLE BY DEFAULT.
    '''
    mCardList = []  #List of cards in the deck.
    mAllCards = []  #All the cards which were originally in the deck.
    
    def __init__(self):
        cardList = []
        for cardSuit in [Card.SUIT_HEARTS,Card.SUIT_CLUBS,Card.SUIT_DIAMONDS,Card.SUIT_SPADES]:
            suitList = []
            for cardValue in [Card.CARD_ACE,Card.CARD_2,Card.CARD_3,Card.CARD_4,Card.CARD_5,Card.CARD_6,Card.CARD_7,Card.CARD_8,Card.CARD_9,Card.CARD_10,Card.CARD_JACK,Card.CARD_QUEEN,Card.CARD_KING]:
                newCard = Card(self,cardSuit,cardValue)
                suitList.append(newCard)
            if(cardSuit in [Card.SUIT_DIAMONDS,Card.SUIT_SPADES]):
                suitList.reverse()
            cardList += suitList
        self.mCardList = cardList
        self.mAllCards = cardList
    
    def shuffle(self):
        'Shuffles the deck'
        random.shuffle(self.mCardList)
    
    def getNextCard(self):
        'Gets the next card from the deck'
        nextCard = self.mCardList.pop(0)
        nextCard.setInDeck(False)
        return nextCard
    
    def isEmpty(self):
        'Boolean, whether the deck is empty.'
        return len(self.mCardList) == 0
    
    def getCard(self,suit,value):
        'Returns the card object for this deck with the specified suit and value.'
        for card in self.mAllCards:
            if(suit == card.getSuit() and value == card.getValue()):
                return card
    
class Hand:
    '''
    Hand of cards, stores a set of cards in an order.
    '''
    mCardList = []
    mPlayer = None
    
    def __init__(self,userObject):
        self.mPlayer = userObject
    
    def shuffle(self):
        'Shuffles a hand'
        random.shuffle(self.mCardList)
    
    def addCard(self,newCard):
        'Adds a new card to the hand'
        self.mCardList.append(newCard)
        
    def sumTotal(self):
        'Returns the sum total of the hand.'
        return sum([card.sumValue() for card in self.mCardList])
    
    def containsCard(self,cardObject):
        'Checks whether a hand contains a specified card'
        return cardObject in self.mCardList

class RandomCard(Function):
    '''
    Returns a random card from a fresh deck.
    '''
    #Name for use in help listing
    mHelpName = "card"
    #Names which can be used to address the function
    mNames = set(["card","random card","randomcard"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Picks a random card from a deck. Format: random_card"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        newDeck = Deck()
        newDeck.shuffle()
        randomCard = newDeck.getNextCard()
        return "I have chosen the " + randomCard.toString() + "."
import pickle
import random


class mod_pokemon:

    def fn_i_choose_you(self,args,client,destination):
        'Picks a random pokemon from generation I to generation IV unless a generation is specified. Format: i_choose_you gen <generation>'
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        randmon = pokemon[random.randint(0,len(pokemon))+1]
        return "I choose you, " + randmon['Name'] + "!"

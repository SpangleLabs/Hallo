import pickle
import random


class mod_pokemon:

    def fn_i_choose_you(self,args,client,destination):
        'Picks a random pokemon from generation I to generation IV unless a generation is specified. Format: i_choose_you gen <generation>'
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        randmon = pokemon[random.randint(0,len(pokemon))+1]
        return "I choose you, " + randmon['Name'] + "!"

    def fn_i(self,args,client,destination):
        'Hacky alias for I_choose_you'
        if('you' in args):
            args = args.split('you')[1]
            return mod_pokemon.fn_i_choose_you(self,args,client,destination)
        else:
            return "Huh?"


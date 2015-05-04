import pickle
import random


class mod_pokemon:

    def fn_pokedex(self,args,client,destination):
        'Returns a random pokedex entry for a given pokemon.'
        args = args.lower()
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        for entry in pokemon:
            if(pokemon[entry]['Name'].lower() == args):
                pokedex = pokemon[entry]['Dex_entries']
                break
        pokedex_entries = []
        for animedexentry in pokedex['Anime']:
            if(pokedex['Anime'][animedexentry]):
                pokedex_entries.append(pokedex['Anime'][animedexentry])
        for gamedexentry in pokedex['Games']:
            if(pokedex['Games'][gamedexentry]):
                pokedex_entries.append(pokedex['Games'][gamedexentry])
        if(len(pokedex_entries)==0):
            return "No available pokedex data."
        return pokedex_entries[random.randint(0,len(pokedex_entries)-1)]

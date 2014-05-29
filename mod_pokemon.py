import pickle
import random


class mod_pokemon:

    def fn_i_choose_you(self,args,client,destination):
        'Picks a random pokemon from generation I to generation IV unless a generation is specified. Format: i_choose_you gen <generation>'
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        randmon = pokemon[random.randint(1,len(pokemon))]
        return "I choose you, " + randmon['Name'] + "!"

    def fn_i(self,args,client,destination):
        'Hacky alias for I_choose_you'
        args = args.lower()
        if('you' in args):
            args = args.split('you')[1]
            return mod_pokemon.fn_i_choose_you(self,args,client,destination)
        else:
            return "Huh?"

    def fn_pick_a_team(self,args,client,destination):
        'Generates a team of pokemon for you.'
        args = args.lower()
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        team = []
        for a in range(6):
            team.append(pokemon[random.randint(1,len(pokemon))]['Name'])
        return "Your team is: " + ', '.join(team[:5]) + ' and ' + team[5] + '.'

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

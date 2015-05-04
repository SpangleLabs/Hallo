import pickle
import random


class mod_pokemon:

    def fn_pick_a_team(self,args,client,destination):
        'Generates a team of pokemon for you.'
        args = args.lower()
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        team = []
        for _ in range(6):
            team.append(pokemon[random.randint(1,len(pokemon))]['Name'])
        return "Your team is: " + ', '.join(team[:5]) + ' and ' + team[5] + '.'

    def fn_fully_evolved_team(self,args,client,destination):
        'Pick a fully evolved pokemon team.'
        fully_evolved = []
        pokemon = pickle.load(open('store/pokemon.p','rb'))
        for mon in pokemon:
            if(len(pokemon[mon]['Evolve_To'])==0):
                fully_evolved.append(pokemon[mon])
        team = []
        for _ in range(6):
            team.append(fully_evolved[random.randint(0,len(fully_evolved))]['Name'])
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

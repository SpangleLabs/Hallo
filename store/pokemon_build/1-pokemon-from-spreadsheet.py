import pickle


#THIS IS THE RAW PASTED DATA FROM SPREADSHEET
#raw_data = '''....'''

list_pokemon = raw_data.split("\n")

pokemondata = {}
for pokemonline in list_pokemon:
	pokemonsplit = pokemonline.split("\t")
	dexnum = pokemonsplit[0]
	name = pokemonsplit[1]
	evolvesfrom = pokemonsplit[2]
	inddata = {'Name':name,'Dex_National':dexnum}
	pokemondata[int(dexnum)] = inddata

	
pickle.dump(pokemondata,open('pokemon.p','wb'))


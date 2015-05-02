import random
import ircbot_chk

class mod_pony:

    def fn_bestpony(self, args, client, destination):
        'Who is bestpony? Format: bestpony'
        arr_ponies = [["Applejack|she", "Fluttershy|she", "Pinkie Pie|she", "Rainbow Dash|she", "Rarity|she", "Twilight Sparkle|she"], ["Princess Cadence|she", "Princess Celestia|she", "Princess Luna|she", "Shining Armor|he"], ["Applebloom|she", "Babs Seed|she", "Scootaloo|she", "Sweetie Belle|she"], ["Big Macintosh|he", "Blossomforth|she", "Cheerilee|she", "Daisy|she", "Derpy Hooves|she", "Dr Hooves|he", "Filthy Rich|he", "Golden Harvest|she", "Granny Smith|she", "Lily|she", "Lotus Blossom|she", "Lyra Heartstrings|she", "Mayor Mare|she", "Minuette|she", "Mr Carrot Cake|he", "Mrs Cup Cake|she", "Nurse Redheart|she", "Pound Cake|he", "Pumpkin Cake|she", "Sweetie Drops|she", "Rose|she"], ["Discord|he", "Fido|he", "Flim|he", "Garble|he", "Gilda|she", "King Sombra|he", "Nightmare Moon|she", "Queen Chrysalis|she", "Rover|he", "Spot|he", "The GREAT and POWERFUL Trixie!|she"], ["Fleetfoot|she", "Soarin|he", "Spitfire|she"], ["DJ-PON3|she", "Donut Joe|he", "Fancy Pants|he", "Fleur de Lis|she", "Hoity Toity|he", "Jet Set|he", "Octavia Melody|she", "Photo Finish|she", "Prince Blueblood|he", "Sapphire Shores|she", "Upper Crust|she"], ["Flitter|she", "Lightning Dust|she", "Stormwalker|she", "Thunderlane|he"], ["Diamond Tiara|she", "Featherweight|he", "Pip Squeak|he", "Silver Spoon|she", "Snails|he", "Snips|he", "Twist|she"], ["Chancellor Puddinghead|she", "Clover the Clever|she", "Commander Hurricane|she", "Princess Platinum|she", "Private Pansy|she", "Smart Cookie|she"], ["Chief Thunderhooves|he", "Crackle|she", "Cranky Doodle Donkey|he", "Gustave Le Grand|he", "Iron Will|he", "Little Strongheart|she", "Madame Leflour|she", "Manny Roar|he", "Matilda|she", "muffinmare|she", "Mulia Mild|she", "Rocky|he", "Sir Lintsalot|he", "Smarty Pants|she", "Spike|he", "Steven Magnet|he", "Zecora|she"], ["Braeburn|he", "Daring Do|she", "Ms. Harshwhinny|she"], ["Angel|he", "Gummy|he", "Opalescence|she", "Owlowiscious|he", "Peewee|he", "Tank|he", "Winona|she"]]
        arr_weights = ["mane6", "mane6", "mane6", "mane6", "mane6", "princess", "princess", "princess", "princess", "cmc", "cmc", "cmc", "ponyville", "ponyville", "villain", "villain", "wonderbolt", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming", "notapony", "other", "pet"]
        arr_categories = ["mane6", "princess", "cmc", "ponyville", "villain", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming", "notapony", "other", "pet"]
        activearray = arr_ponies[arr_categories.index(arr_weights[random.randint(0,len(arr_weights)-1)])]
        bestpony = activearray[random.randint(0,len(activearray)-1)]
        if(client.lower() == 'd000242'):
            bestpony = "Pinkie Pie|she"
        arr_premessage = ["Obviously {X} is best pony because ", "Well, everyone knows that {X} is bestpony, I mean ", "The best pony is certainly {X}, ", "There's no debate, {X} is bestpony, ", "Bestpony? You must be talking about {X}, "]
        arr_postmessage = ["{Y}'s just such a distinctive character.", "{Y} really just stands out.", "{Y} really makes the show worth watching for me.", "{Y} stands up for what's best for everypony.", "I can really identify with that character.", "I just love the colourscheme I suppose.", "I mean, why not?"]
        num_premessage = len(arr_premessage)
        num_postmessage = len(arr_postmessage)
        randpre = random.randint(0,num_premessage-1)
        randpost = random.randint(0,num_postmessage-1)
        return arr_premessage[randpre].replace("{X}",bestpony.split("|")[0]) + arr_postmessage[randpost].replace("{Y}",bestpony.split("|")[1])

    def fn_cupcake(self, args, client, destination):
        'Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>'
        if(args==''):
            return "You must specify a recipient for the cupcake."
        elif(len(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],[args.split()[0]]))!=0):
            if(len(args.split()) >= 2):
                return '\x01ACTION gives ' + args.split()[0] + ' a ' + ' '.join(args.split()[1:]) + ' cupcake, from ' + client + '.\x01'
            else:
                return '\x01ACTION gives ' + args.split()[0] + ' a cupcake, from ' + client + '.\x01'
        else:
            return 'No one called "' + args.split()[0] + '" is online.'


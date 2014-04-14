

class mod_pony:

    def fn_pony_ep(self, args, client, destination):
        'Chooses a pony episode to watch at random. Format: "pony_ep" to pick a random pony episode, "pony_ep song" to pick a random pony episode which includes a song.'
        episodes = ["S01E01 - Episode 1","S01E02 - Episode 2","S01E03 - The Ticket Master","S01E04 - Applebuck Season","S01E05 - Griffon the Brush-Off","S01E06 - Boast Busters","S01E07 - Dragonshy","S01E08 - Look Before You Sleep","S01E09 - Bridle Gossip","S01E10 - Swarm of the Century","S01E11 - Winter Wrap-Up","S01E12 - Call of the Cutie","S01E13 - Fall Weather Friends","S01E14 - Suited for Success","S01E15 - Feeling Pinkie Keen","S01E16 - Sonic Rainboom","S01E17 - Stare Master","S01E18 - The Show Stoppers","S01E19 - A Dog and Pony Show","S01E20 - Green is not your Color","S01E21 - Over a Barrel","S01E22 - A Bird in the Hoof","S01E23 - The Cutie Mark Chronicles","S01E24 - Owls well that Ends well","S01E25 - Party of One","S01E26 - The Best Night Ever","S02E01 - Return of Harmony Part 1","S02E02 - Return of Harmony Part 2","S02E03 - Lesson Zero","S02E04 - Luna Eclipsed","S02E05 - Sisterhooves Social","S02E06 - The Cutie Pox","S02E07 - May the Best Pet Win","S02E08 - The Mysterious Mare Do Well","S02E09 - Sweet and Elite","S02E10 - Secret of My Excess","S02E11 - Hearth's Warming Eve","S02E12 - Family Appreciation Day","S02E13 - Baby Cakes","S02E14 - The Last Roundup","S02E15 - The Super Speedy Cider Squeezy 6000","S02E16 - Read it and Weep","S02E17 - Hearts and Hooves day","S02E18 - A Friend In Deed","S02E19 - Putting Your Hoof Down","S02E20 - It's About Time","S02E21 - Dragon Quest","S02E22 - Hurricane Fluttershy","S02E23 - Ponyville Confidential","S02E24 - MMMystery on the Friendship Express","S02E25 - Canterlot Wedding Part 1","S02E26 - Canterlot Wedding Part 2","S03E01 - The Crystal Empire Part 1","S03E02 - The Crystal Empire Part 2","S03E03 - Too Many Pinkie Pies","S03E04 - One Bad Apple","S03E05 - Magic Duel","S03E06 - Sleepless in Ponyville","S03E07 - Wonderbolts Academy","S03E08 - Apple Family Reunion","S03E09 - Spike at your Service","S03E10 - Keep Calm and Flutter On","S03E11 - Just for Sidekicks","S03E12 - Games Ponies Play","S03E13 - Magical Mystery Cure"]
        songepisodes = ["S01E01 - Episode 1","S01E02 - Episode 2","S01E03 - The Ticket Master","S01E11 - Winter Wrap-Up","S01E14 - Suited for Success","S01E18 - The Show Stoppers","S01E23 - The Cutie Mark Chronicles","S01E26 - The Best Night Ever","S02E07 - May the Best Pet Win","S02E09 - Sweet and Elite","S02E11 - Hearth's Warming Eve","S02E13 - Baby Cakes","S02E15 - The Super Speedy Cider Squeezy 6000","S02E17 - Hearts and Hooves day","S02E18 - A Friend In Deed","S02E25 - Canterlot Wedding Part 1","S02E26 - Canterlot Wedding Part 2","S03E01 - The Crystal Empire Part 1","S03E02 - The Crystal Empire Part 2","S03E04 - One Bad Apple","S03E08 - Apple Family Reunion","S03E13 - Magical Mystery Cure"]
        if(args.lower()!="song"):
           numepisodes = len(episodes)
           rand = random.randint(0,numepisodes-1)
           episode = episodes[rand]
        else:
           numepisodes = len(songepisodes)
           rand = random.randint(0,numepisodes-1)
           episode = songepisodes[rand]
        return 'You should choose "' + episode + '."'

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
        num_ponies = len(arr_ponies)
        num_premessage = len(arr_premessage)
        num_postmessage = len(arr_postmessage)
        randpony = random.randint(0,num_ponies-1)
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


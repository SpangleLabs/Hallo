episodes = ["S01E01 - Episode 1", "S01E02 - Episode 2", "S01E03 - The Ticket Master", "S01E04 - Applebuck Season",
            "S01E05 - Griffon the Brush-Off", "S01E06 - Boast Busters", "S01E07 - Dragonshy",
            "S01E08 - Look Before You Sleep", "S01E09 - Bridle Gossip", "S01E10 - Swarm of the Century",
            "S01E11 - Winter Wrap-Up", "S01E12 - Call of the Cutie", "S01E13 - Fall Weather Friends",
            "S01E14 - Suited for Success", "S01E15 - Feeling Pinkie Keen", "S01E16 - Sonic Rainboom",
            "S01E17 - Stare Master", "S01E18 - The Show Stoppers", "S01E19 - A Dog and Pony Show",
            "S01E20 - Green is not your Color", "S01E21 - Over a Barrel", "S01E22 - A Bird in the Hoof",
            "S01E23 - The Cutie Mark Chronicles", "S01E24 - Owls well that Ends well", "S01E25 - Party of One",
            "S01E26 - The Best Night Ever"]
episodes += ["S02E01 - Return of Harmony Part 1", "S02E02 - Return of Harmony Part 2", "S02E03 - Lesson Zero",
             "S02E04 - Luna Eclipsed", "S02E05 - Sisterhooves Social", "S02E06 - The Cutie Pox",
             "S02E07 - May the Best Pet Win", "S02E08 - The Mysterious Mare Do Well", "S02E09 - Sweet and Elite",
             "S02E10 - Secret of My Excess", "S02E11 - Hearth's Warming Eve", "S02E12 - Family Appreciation Day",
             "S02E13 - Baby Cakes", "S02E14 - The Last Roundup", "S02E15 - The Super Speedy Cider Squeezy 6000",
             "S02E16 - Read it and Weep", "S02E17 - Hearts and Hooves day", "S02E18 - A Friend In Deed",
             "S02E19 - Putting Your Hoof Down", "S02E20 - It's About Time", "S02E21 - Dragon Quest",
             "S02E22 - Hurricane Fluttershy", "S02E23 - Ponyville Confidential",
             "S02E24 - MMMystery on the Friendship Express", "S02E25 - Canterlot Wedding Part 1",
             "S02E26 - Canterlot Wedding Part 2"]
episodes += ["S03E01 - The Crystal Empire Part 1", "S03E02 - The Crystal Empire Part 2",
             "S03E03 - Too Many Pinkie Pies", "S03E04 - One Bad Apple", "S03E05 - Magic Duel",
             "S03E06 - Sleepless in Ponyville", "S03E07 - Wonderbolts Academy", "S03E08 - Apple Family Reunion",
             "S03E09 - Spike at your Service", "S03E10 - Keep Calm and Flutter On", "S03E11 - Just for Sidekicks",
             "S03E12 - Games Ponies Play", "S03E13 - Magical Mystery Cure"]
episodes += ["S04E01 - Princess Twilight Sparkle (Part 1)", "S04E02 - Princess Twilight Sparkle (Part 2)",
             "S04E03 - Castle Mane-ia", "S04E04 - Daring Don't", "S04E05 - Flight to the Finish",
             "S04E06 - Power Ponies", "S04E07 - Bats!", "S04E08 - Rarity Takes Manehattan", "S04E09 - Pinkie Apple Pie",
             "S04E10 - Rainbow Falls", "S04E11 - Three's a Crowd", "S04E12 - Pinkie Pride", "S04E13 - Simple Ways",
             "S04E14 - Filli Vanilli", "S04E15 - Twilight Time", "S04E16 - It Aint's Easy Being Breezies",
             "S04E17 - Somepony to Watch Over Me", "S04E18 - Maud Pie", "S04E19 - For Whom The Sweetie Belle Tolls",
             "S04E20 - Leap of Faith", "S04E21 - Testing Testing 1, 2, 3", "S04E22 - Trade Ya!",
             "S04E23 - Inspiration Manifestation", "S04E24 - Equestria Games", "S04E25 - Twilight's Kingdom (Part 1)",
             "S04E26 - Twilight's Kingdom (Part 2)"]
episodes += ["S05E01 - The Cutie Map (Part 1)", "S05E02 - The Cutie Map (Part 2)", "S05E03 - Castle Sweet Castle",
             "S05E04 - Bloom & Gloom", "S05E05 - Tanks for the Memories"]

songepisodes = ["S01E01 - Episode 1", "S01E02 - Episode 2", "S01E03 - The Ticket Master", "S01E11 - Winter Wrap-Up",
                "S01E14 - Suited for Success", "S01E18 - The Show Stoppers", "S01E23 - The Cutie Mark Chronicles",
                "S01E26 - The Best Night Ever"]
songepisodes += ["S02E07 - May the Best Pet Win", "S02E09 - Sweet and Elite", "S02E11 - Hearth's Warming Eve",
                 "S02E13 - Baby Cakes", "S02E15 - The Super Speedy Cider Squeezy 6000",
                 "S02E17 - Hearts and Hooves day", "S02E18 - A Friend In Deed", "S02E25 - Canterlot Wedding Part 1",
                 "S02E26 - Canterlot Wedding Part 2"]
songepisodes += ["S03E01 - The Crystal Empire Part 1", "S03E02 - The Crystal Empire Part 2", "S03E04 - One Bad Apple",
                 "S03E08 - Apple Family Reunion", "S03E13 - Magical Mystery Cure"]
songepisodes += ["S04E05 - Flight to the Finish", "S04E07 - Bats!", "S04E08 - Rarity Takes Manehattan",
                 "S04E09 - Pinkie Apple Pie", "S04E11 - Three's A Crowd", "S04E12 - Pinkie Pride",
                 "S04E14 - Filli Vanilli", "S04E20 - Leap of Faith", "S04E21 - Testing Testing 1, 2, 3",
                 "S04E25 - Twilight's Kingdom (Part 1)", "S04E26 - Twilight's Kingdom (Part 2)"]
songepisodes += ["S05E01 - The Cutie Map (Part 1)", "S05E03 - Castle Sweet Castle", "S05E05 - Tanks for the Memories"]

print("<!DOCTYPE pony_episodes SYSTEM \"pony_episodes.dtd\"><pony_episodes>")
for episode in episodes:
    print("\t<pony_episode>")
    season = int(episode[1:3])
    print("\t\t<season>" + str(season) + "</season>")
    episodeNum = int(episode[4:6])
    print("\t\t<episode>" + str(episodeNum) + "</episode>")
    fullCode = episode[:6]
    print("\t\t<full_code>" + fullCode + "</full_code>")
    name = ' '.join(episode.split()[2:]).replace("&", "&amp;")
    print("\t\t<name>" + name + "</name>")
    if episode in songepisodes:
        print("\t\t<song>True</song>")
    else:
        print("\t\t<song>False</song>")
    print("\t</pony_episode>")
print("</pony_episodes>")

from Function import Function
from inc.commons import Commons

class E621(Function):
    '''
    Returns a random image from e621
    '''
    #Name for use in help listing
    mHelpName = "e621"
    #Names which can be used to address the function
    mNames = set(["e621"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random e621 result using the search you specify. Format: e621 <tags>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        searchResult = self.getRandomLinkResult(line)
        if(searchResult == None):
            return "No results."
        else:
            link = "http://e621.net/post/show/"+str(searchResult['id'])
            if(searchResult['rating']=='e'):
                rating = "(Explicit)"
            elif(searchResult['rating']=="q"):
                rating = "(Questionable)"
            elif(searchResult['rating']=="s"):
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            lineResponse = line.strip()
            return "e621 search for \""+lineResponse+"\" returned: "+link+" "+rating
    
    def getRandomLinkResult(self,search):
        'Gets a random link from the e621 api.'
        lineClean = search.replace(' ','%20')
        url = 'https://e621.net/post/index.json?tags=order:random%20score:%3E0%20'+lineClean+'%20&limit=1'
        returnList = Commons.loadUrlJson(url)
        if(len(returnList)==0):
            return None
        else:
            result = returnList[0]
            return result

class RandomPorn(Function):
    '''
    Returns a random explicit image from e621
    '''
    #Name for use in help listing
    mHelpName = "random porn"
    #Names which can be used to address the function
    mNames = set(["random porn","randomporn"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random explicit e621 result using the search you specify. Format: random porn <tags>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineUnclean = line.strip()+" -rating:s"
        functionDispatcher = userObject.getServer().getHallo().getFunctionDispatcher()
        e621Class = functionDispatcher.getFunctionByName("e621")
        e621Object = functionDispatcher.getFunctionObject(e621Class)
        searchResult = e621Object.getRandomLinkResult(lineUnclean)
        if(searchResult == None):
            return "No results."
        else:
            link = "http://e621.net/post/show/"+str(searchResult['id'])
            if(searchResult['rating']=='e'):
                rating = "(Explicit)"
            elif(searchResult['rating']=="q"):
                rating = "(Questionable)"
            elif(searchResult['rating']=="s"):
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            lineResponse = line.strip()
            return "e621 search for \""+lineResponse+"\" returned: "+link+" "+rating

class Butts(Function):
    '''
    Returns a random butt from e621
    '''
    #Name for use in help listing
    mHelpName = "butts"
    #Names which can be used to address the function
    mNames = set(["random butt","butts","butts!","butts."])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random image from e621 for the search \"butt\". Format: butts"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        functionDispatcher = userObject.getServer().getHallo().getFunctionDispatcher()
        e621Class = functionDispatcher.getFunctionByName("e621")
        e621Object = functionDispatcher.getFunctionObject(e621Class)
        searchResult = e621Object.getRandomLinkResult("butt")
        if(searchResult == None):
            return "No results."
        else:
            link = "http://e621.net/post/show/"+str(searchResult['id'])
            if(searchResult['rating']=='e'):
                rating = "(Explicit)"
            elif(searchResult['rating']=="q"):
                rating = "(Questionable)"
            elif(searchResult['rating']=="s"):
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            return "e621 search for \"butt\" returned: "+link+" "+rating

class Fursona(Function):
    '''
    Generates a random fursona
    '''
    #Name for use in help listing
    mHelpName = "fursona"
    #Names which can be used to address the function
    mNames = set(["fursona","sona","random fursona","random sona"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Generates your new fursona. Format: fursona"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        adjective = ["eldritch","neon green","angelic","ghostly","scene","emo","hipster","alien","sweaty","OBSCENELY BRIGHT YELLOW","spotted","hairy","glowing","pastel pink","glittering blue","golden","shimmering red","robotic","black","goth","elegant","white","divine","striped","radioactive","red and green","slimy","slime","garbage","albino","skeleton","petite","swamp","aquatic","vampire","bright pink and yellow","mossy","stone","gray","fairy","zombie","pastel","mint green","giant","big pink","tiny pink","big white","tiny white","tiny black","translucent","glistening","glittering black","shimmering white","iridescent","glass","silver","jewel-encrusted","fuschia","purple","tiny purple","lilac","lavender","shimmering lilac","sparkling purple","tiny blue","heavenly","gilded","holy","blue and white striped","black and orange spotted","black and red","black and orange","ancient","green","purple and blue","pink and blue","candy","abyssal","floral","candle","melanistic","punk","ethereal","unholy","celestial","cyan","cream","cream and pink","cream and brown","yellow","black and pink","magenta","speckled","tiger-striped","chocolate","pastel goth","vintage","glossy black","glossy white","glossy gray","glossy blue","glossy pink","shimmery gray","glossy yellow","magma","plastic","leucistic","piebald"]
        animal = ["kestrel.","goat.","sheep.","dragon.","platypus.","blobfish.","hydra.","wolf.","fox.","sparkledog.","cow.","bull.","cat.","tiger.","panther.","hellhound.","spider.","beagle.","pomeranian.","whale.","hammerhead shark.","snake.","hyena.","lamb.","pony.","horse.","pup.","swan.","pigeon.","dove.","fennec fox.","fish.","rat.","possum.","hamster.","deer.","elk.","reindeer.","cheetah.","ferret.","bear.","panda.","koala.","kangaroo.","skink.","lizard.","iguana.","cerberus.","turtle.","raven.","cardinal.","bluejay.","antelope.","buffalo.","rabbit.","bunny.","frog.","newt.","salamander.","cobra.","coyote.","jellyfish.","bee.","wasp.","dinosaur.","bat.","worm.","chicken.","eel.","tiger.","sloth.","seal.","vulture.","barghest.","hedgehog.","peacock.","anglerfish.","dolphin.","liger.","llama.","alpaca.","walrus.","mantis.","ladybug.","penguin.","flamingo.","civet.","pudu.","crab.","maine coon.","fawn.","siamese.","amoeba.","owl.","unicorn.","crocodile.","alligator.","chihuahua.","great dane.","dachshund.","corgi.","rooster.","sparrow.","wyrm.","slug.","snail.","seagull.","badger.","gargoyle.","scorpion.","boa.","axolotl."]
        description1 = ["it constantly drips with a tar-like black substance.","it enjoys performing occult rituals with friends.","it is a communist.","a golden halo floats above its head.","it wears a mcdonalds uniform because it works at mcdonalds.","it carries a nail bat.","it wears louboutin heels.","it has two heads.","it has an unknowable amount of eyes.","it drools constantly.","its tongue is bright green.","it has numerous piercings.","it is a cheerleader.","it is a farmhand.","when you see it you are filled with an ancient fear.","it wears a toga.","it is made of jelly.","it has incredibly long and luxurious fur.","it uses reddit but won't admit it.","it glows softly and gently- evidence of a heavenly being.","it is a ghost.","it dresses like a greaser.","crystals grow from its flesh.","it rides motorcycles.","it wears incredibly large and impractical sunglasses.","it instagrams its starbucks drinks.","it is a hired killer.","where its tail should be is just another head.","it dwells in a bog.","it is wet and dripping with algae.","it runs a blog dedicated to different types of planes throughout history.","it worships the moon.","it comes from a long line of royalty.","it frolics in flowery meadows.","it wears a ballerina's outfit.","it wears a neutral milk hotel t-shirt with red fishnets and nothing else.","it wears a lot of eye makeup.","it won't stop sweating.","it has far too many teeth and they are all sharp.","it is a tattoo artist.","it is shaking.","it is a witch.","it wears scarves all the time.","to look into its eyes is to peer into a distant abyss.","mushrooms grow from its skin.","its face is actually an electronic screen.","it loves to wear combat boots with cute stickers all over them.","it comes from space.","it is a knife collector.","it flickers in and out of this plane of reality.","it wishes it were a butt.","its eyes are red.","it is the most beautiful thing you have ever seen.","it loves strawberry milkshakes.","it cries all the time and can't really do much about it.","it lives alone in a dense forgotten wilderness.","it wears big christmas sweaters year-round.","it floats about a foot off of the ground.","it loves trash.","it has demonic wings.","it has a cutie mark of a bar of soap.","it is melting.","it wears opulent jewelry of gold and gemstones.","it has a hoard of bones.","it has ram horns.","it has a forked tongue.","it wears frilly dresses.","it has antlers.","it is a nature spirit.","its back is covered in candles which flicker ominously.","it wears a leather jacket with lots of patches.","it wears a snapback.","it has a tattoo that says 'yolo'.","electricity flickers through the air surrounding it.","it is a fire elemental.","it consumes only blood.","it works at an adorable tiny bakery.","it is a professional wrestler.","instead of eyes there are just more ears.","it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.","it works out.","it wishes it were a tree.","it is always blushing.","it uses ancient and powerful magic.","it loves raw meat.","it is always smiling.","it can fire lasers from its eyes.","a small rainbutt follows it everywhere.","it is made of glass.","fireflies circle it constantly.","it is always accompanied by glowing orbs of light.","it has human legs.","water drips from it constantly.","it has golden horns.","it loves gore.","it lives in a cave with its parents.","its purse costs more than most people's cars.","it always shivers even when it's not cold.","it has tentacles.","it never blinks.","it only listens to metal.","it wears a golden crown.","it wears a white sundress.","it has green hair pulled up into two buns.","its body is covered in occult sigils and runes which pulse ominously.","it loves to devour the rotting plant matter covering the forest floor.","it wears a plain white mask.","its eyes flash multiple colors rapidly.","it loves to wear nail polish but applies it messily.","it runs a jimmy carter fanblog.","it is a surfer.","it only wears hawaiian shirts.","everything it wears is made out of denim.","it has long braided hair.","it calls everybody comrade.","it lures men to their deaths with its beautiful voice.","it has braces.","it has full sleeve tattoos.","it dresses like a grandpa.","smoke pours from its mouth.","it is a makeup artist.","it dresses like a pinup girl.","it has only one large eye.","it plays the harp.","it has very long hair with many flowers in it.","it has a cyan buzzcut.","it is a garden spirit.","it has fangs capable of injecting venom.","numerous eyeballs float around it. watching. waiting.","it loves to play in the mud.","it wears a surgical mask.","its eyes are pitch black and cause those who look directly into them for too long to slowly grow older.","it wears numerous cute hairclips.","it has a very large tattoo of the 'blockbuster' logo.","it is constantly covered in honey that drips on everything and pools beneath it.","it wears a cherry-themed outfit.","it has heterochromia.","it is heavily scarred.","in place of a head it has a floating cube that glows and pulses softly.","it seems to be glitching.","it does not have organs- instead it is full of flowers.","its insides are glowing.","it is a skateboarder.","it is a superwholock blogger.","it is a skilled glass-blower.","it has a pet of the same species as itself.","it is the leader of an association of villains.","it wears a black leather outfit.","its pupils are slits.","it wears a crop top with the word OATMEAL in all caps.","it only wears crop tops and high waisted shorts.","it is always giving everyone a suspicious look.","it has a septum piercing.","instead of talking it just says numbers.","it is an internet famous scene queen.","its eyes are way too big to be normal.","it has super obvious tan lines.","it wears a maid outfit.","it is an emissary from hell.","its eyes have multiple pupils in them.","it has an impractically large sword.","it is a magical girl.","it has a scorpion tail.","it is a biologist specializing in marine invertebrates.","it runs. everywhere. all the time.","it is an esteemed fashion designer for beings with 6 or more limbs.","it wears short shorts that say CLAM.","it can't stop knitting.","it is always coated in glitter.","it worships powerful dolphin deities.","it has slicked back hair.","it has a thick beard.","it has a long braided beard plaited with ribbons.","it is a viking.","it wears a parka.","its outfit is completely holographic.","it wears an oversized pearl necklace.","it has stubble.","it carries a cellphone with a ridiculous amount of charms and keychains.","it wears crocs.","it has a hoard of gems and gold that was pillaged from innocent villagers.","it robs banks.","its facial features are constantly shifting.","it works as a librarian in hell.","it wears a fedora."]
        description2 = ["it constantly drips with a tar-like black substance.","it enjoys performing occult rituals with friends.","it is a communist.","a golden halo floats above its head.","it wears a mcdonalds uniform because it works at mcdonalds.","it carries a nail bat.","it wears louboutin heels.","it has two heads.","it has an unknowable amount of eyes.","it drools constantly.","its tongue is bright green.","it has numerous piercings.","it is a cheerleader.","it is a farmhand.","when you see it you are filled with an ancient fear.","it wears a toga.","it is made of jelly.","it has incredibly long and luxurious fur.","it uses reddit but won't admit it.","it glows softly and gently- evidence of a heavenly being.","it is a ghost.","it dresses like a greaser.","crystals grow from its flesh.","it rides motorcycles.","it wears incredibly large and impractical sunglasses.","it instagrams its starbucks drinks.","it is a hired killer.","where its tail should be is just another head.","it dwells in a bog.","it is wet and dripping with algae.","it runs a blog dedicated to different types of planes throughout history.","it worships the moon.","it comes from a long line of royalty.","it frolics in flowery meadows.","it wears a ballerina's outfit.","it wears a neutral milk hotel t-shirt with red fishnets and nothing else.","it wears a lot of eye makeup.","it won't stop sweating.","it has far too many teeth and they are all sharp.","it is a tattoo artist.","it is shaking.","it is a witch.","it wears scarves all the time.","to look into its eyes is to peer into a distant abyss.","mushrooms grow from its skin.","its face is actually an electronic screen.","it loves to wear combat boots with cute stickers all over them.","it comes from space.","it is a knife collector.","it flickers in and out of this plane of reality.","it wishes it were a butt.","its eyes are red.","it is the most beautiful thing you have ever seen.","it loves strawberry milkshakes.","it cries all the time and can't really do much about it.","it lives alone in a dense forgotten wilderness.","it wears big christmas sweaters year-round.","it floats about a foot off of the ground.","it loves trash.","it has demonic wings.","it has a cutie mark of a bar of soap.","it is melting.","it wears opulent jewelry of gold and gemstones.","it has a hoard of bones.","it has ram horns.","it has a forked tongue.","it wears frilly dresses.","it has antlers.","it is a nature spirit.","its back is covered in candles which flicker ominously.","it wears a leather jacket with lots of patches.","it wears a snapback.","it has a tattoo that says 'yolo'.","electricity flickers through the air surrounding it.","it is a fire elemental.","it consumes only blood.","it works at an adorable tiny bakery.","it is a professional wrestler.","instead of eyes there are just more ears.","it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.","it works out.","it wishes it were a tree.","it is always blushing.","it uses ancient and powerful magic.","it loves raw meat.","it is always smiling.","it can fire lasers from its eyes.","a small rainbutt follows it everywhere.","it is made of glass.","fireflies circle it constantly.","it is always accompanied by glowing orbs of light.","it has human legs.","water drips from it constantly.","it has golden horns.","why is it always covered in blood?","it loves gore.","it lives in a cave with its parents.","its purse costs more than most people's cars.","it always shivers even when it's not cold.","it has tentacles.","it never blinks.","it only listens to metal.","it wears a golden crown.","it wears a white sundress.","it has green hair pulled up into two buns.","its body is covered in occult sigils and runes which pulse ominously.","it loves to devour the rotting plant matter covering the forest floor.","it wears a plain white mask.","its eyes flash multiple colors rapidly.","you are afraid.","it loves to wear nail polish but applies it messily.","it runs a jimmy carter fanblog.","it is a surfer.","it only wears hawaiian shirts.","everything it wears is made out of denim.","it has long braided hair.","it calls everybody comrade.","it lures men to their deaths with its beautiful voice.","it has braces.","it has full sleeve tattoos.","it dresses like a grandpa.","smoke pours from its mouth.","it is a makeup artist.","it dresses like a pinup girl.","it has only one large eye.","it plays the harp.","it has very long hair with many flowers in it.","it has a cyan buzzcut.","it is a garden spirit.","it has fangs capable of injecting venom.","numerous eyeballs float around it. watching. waiting.","it loves to play in the mud.","it wears a surgical mask.","its eyes are pitch black and cause those who look directly into them for too long to slowly grow older.","it wears numerous cute hairclips.","it has a very large tattoo of the 'blockbuster' logo.","it is constantly covered in honey that drips on everything and pools beneath it.","it wears a cherry-themed outfit.","it has heterochromia.","it is heavily scarred.","in place of a head it has a floating cube that glows and pulses softly.","it seems to be glitching.","its insides are glowing.","it does not have organs- instead it is full of flowers.","it is a skateboarder.","it is a superwholock blogger.","it is a skilled glass-blower.","it has a pet of the same species as itself.","it is the leader of an association of villains.","it wears a black leather outfit.","its pupils are slits..","it wears a crop top with the word OATMEAL in all caps.","it only wears crop tops and high waisted shorts.","it is always giving everyone a suspicious look.","it has a septum piercing.","its hair is beehive style. not an actual beehive.","instead of talking it just says numbers.","it has a halo. over its ass.","it is an internet famous scene queen.","its eyes are way too big to be normal.","it has super obvious tan lines.","it wears a maid outfit.","it is an emissary from hell.","its eyes have multiple pupils in them.","there are scorpions everywhere.","it has an impractically large sword.","it is a magical girl.","it has a scorpion tail.","it is a biologist specializing in marine invertebrates.","it runs. everywhere. all the time.","it is an esteemed fashion designer for beings with 6 or more limbs.","it wears short shorts that say CLAM.","it can't stop knitting.","it is always coated in glitter.","it worships powerful dolphin deities.","it has slicked back hair.","it has a thick beard.","it has a long braided beard plaited with ribbons.","it is a viking.","it wears a parka.","its outfit is completely holographic.","it wears an oversized pearl necklace.","it has stubble.","it carries a cellphone with a ridiculous amount of charms and keychains.","Welcome to Hell! Welcome to Hell!","it wears crocs.","it has a hoard of gems and gold that was pillaged from innocent villagers.","it robs banks and its partner in crime is the next fursona you generate.","its facial features are constantly shifting.","it works as a librarian in hell.","it wears a fedora."]
        result = "Your new fursona is: "+Commons.getRandomChoice(adjective)+" "+Commons.getRandomChoice(animal)+" "+Commons.getRandomChoice(description1)+" "+Commons.getRandomChoice(description2)
        return result
    

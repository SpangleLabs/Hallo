from Function import Function
from inc.commons import Commons


class Longcat(Function):
    """
    Draws a classic longcat
    """
    # Name for use in help listing
    mHelpName = "longcat"
    # Names which can be used to address the function
    mNames = {"longcat", "ascii longcat"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Make a longcat! Format: longcat <length>"
    
    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Make a longcat! Format: longcat <length>"""
        try:
            longcatSegments = int(line)
        except ValueError:
            longcatSegments = 5
        longcatHead = r'''    /\___/\
   /       \
  |  #    # |
  \     @   |
   \   _|_ /
   /       \______
  / _______ ___   \
  |_____   \   \__/
  |    \__/
'''
        longcatSegment = '   |       |\n'
        longcatTail = r'''   /        \
  /   ____   \
  |  /    \  |
  | |      | |
 /  |      |  \ 
 \__/      \__/'''
        longcat = longcatHead + longcatSegment * longcatSegments + longcatTail
        longcat += '\n Longcat is L' + 'o' * longcatSegments + 'ng!'
        return longcat


class Deer(Function):
    """
    Draws an ascii deer
    """
    # Name for use in help listing
    mHelpName = "deer"
    # Names which can be used to address the function
    mNames = {"deer", "ascii deer"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Ascii art deer. Format: deer"
    
    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """ascii art deer. Format: deer"""
        deer = r'''   /|       |\
`__\\       //__'
   ||      ||
 \__`\     |'__/
   `_\\   //_'
   _.,:---;,._
   \_:     :_/
     |@. .@|
     |     |
     ,\.-./ \
     ;;`-'   `---__________-----.-.
     ;;;                         \_\
     ';;;                         |
      ;    |                      ;
       \   \     \        |      /
        \_, \    /        \     |\
          |';|  |,,,,,,,,/ \    \ \_
          |  |  |           \   /   |
          \  \  |           |  / \  |
           | || |           | |   | |
           | || |           | |   | |
           | || |           | |   | |
           |_||_|           |_|   |_|
          /_//_/           /_/   /_/'''
        return deer


class Dragon(Function):
    """
    Draws an ascii dragon
    """
    # Name for use in help listing
    mHelpName = "dragon"
    # Names which can be used to address the function
    mNames = {"dragon", "ascii dragon"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Prints ascii dragon. Format: dragon"
    
    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Prints ascii dragon. Format: dragon"""
        dragonDeer = r'''hmm.. nah. have another deer.
       ""\/ \/""
         "\__/"
          (oo)
 -. ______-LJ
  ,'        |
  |.____..  /
  \\      /A\
  |A      |//'''
        dragonOne = r'''                     _ _
              _     //` `\
          _,-"\%   // /``\`\
     ~^~ >__^  |% // /  } `\`\
            )  )%// / }  } }`\`\
           /  (%/'/.\_/\_/\_/\`/
          (    '         `-._`
           \   ,     (  \   _`-.__.-;%>
          /_`\ \      `\ \." `-..-'`
         ``` /_/`"-=-'`/_/
    jgs     ```       ```'''
        dragonTwo = r'''           ____ __
          { --.\  |          .)%%%)%%
           '-._\\ | (\___   %)%%(%%(%%%
               `\\|{/ ^ _)-%(%%%%)%%;%%%
           .'^^^^^^^  /`    %%)%%%%)%%%'
  jgs     //\   ) ,  /       '%%%%(%%'
    ,  _.'/  `\<-- \<
     `^^^`     ^^   ^^'''
        rand = Commons.getRandomInt(0, 100)[0]
        if rand == 15:
            dragon = dragonDeer
        elif rand % 2 == 0:
            dragon = dragonOne
        else:
            dragon = dragonTwo
        return dragon


class Train(Function):
    """
    Draws an ascii train
    """
    # Name for use in help listing
    mHelpName = "train"
    # Names which can be used to address the function
    mNames = {"train", "ascii train"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Prints ascii train. Format: train"
    
    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Prints ascii train. Format: train"""
        train = r'''chugga chugga, chugga chugga, woo woo!
            ____.-==-, _______  _______  _______  _______  _..._
           {"""""LILI|[" " "'"]['""'"""][''"""'']["" """"][LI LI]
  ^#^#^#^#^/_OO====OO`'OO---OO''OO---OO''OO---OO''OO---OO`'OO-OO'^#^#^#^
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
        return train

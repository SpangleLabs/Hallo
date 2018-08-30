from Function import Function
from inc.Commons import Commons


class Longcat(Function):
    """
    Draws a classic longcat
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "longcat"
        # Names which can be used to address the function
        self.names = {"longcat", "ascii longcat"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Make a longcat! Format: longcat <length>"

    def run(self, event):
        """Make a longcat! Format: longcat <length>"""
        try:
            segments = int(event.command_args)
        except ValueError:
            segments = 5
        long_cat_head = r'''    /\___/\
   /       \
  |  #    # |
  \     @   |
   \   _|_ /
   /       \______
  / _______ ___   \
  |_____   \   \__/
  |    \__/
'''
        long_cat_segment = '   |       |\n'
        long_cat_tail = r'''   /        \
  /   ____   \
  |  /    \  |
  | |      | |
 /  |      |  \ 
 \__/      \__/'''
        longcat = long_cat_head + long_cat_segment * segments + long_cat_tail
        longcat += "\n Longcat is L{}ng!".format("o"*segments)
        return longcat


class Deer(Function):
    """
    Draws an ascii deer
    """
    
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "deer"
        # Names which can be used to address the function
        self.names = {"deer", "ascii deer"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Ascii art deer. Format: deer"

    def run(self, event):
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
    
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "dragon"
        # Names which can be used to address the function
        self.names = {"dragon", "ascii dragon"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Prints ascii dragon. Format: dragon"

    def run(self, event):
        """Prints ascii dragon. Format: dragon"""
        dragon_deer = r'''hmm.. nah. have another deer.
       ""\/ \/""
         "\__/"
          (oo)
 -. ______-LJ
  ,'        |
  |.____..  /
  \\      /A\
  |A      |//'''
        dragon_one = r'''                     _ _
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
        dragon_two = r'''           ____ __
          { --.\  |          .)%%%)%%
           '-._\\ | (\___   %)%%(%%(%%%
               `\\|{/ ^ _)-%(%%%%)%%;%%%
           .'^^^^^^^  /`    %%)%%%%)%%%'
  jgs     //\   ) ,  /       '%%%%(%%'
    ,  _.'/  `\<-- \<
     `^^^`     ^^   ^^'''
        rand = Commons.get_random_int(0, 100)[0]
        if rand == 15:
            dragon = dragon_deer
        elif rand % 2 == 0:
            dragon = dragon_one
        else:
            dragon = dragon_two
        return dragon


class Train(Function):
    """
    Draws an ascii train
    """
    
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "train"
        # Names which can be used to address the function
        self.names = {"train", "ascii train"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Prints ascii train. Format: train"

    def run(self, event):
        """Prints ascii train. Format: train"""
        train = r'''chugga chugga, chugga chugga, woo woo!
            ____.-==-, _______  _______  _______  _______  _..._
           {"""""LILI|[" " "'"]['""'"""][''"""'']["" """"][LI LI]
  ^#^#^#^#^/_OO====OO`'OO---OO''OO---OO''OO---OO''OO---OO`'OO-OO'^#^#^#^
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
        return train

from hallo.function import Function
from hallo.inc.commons import Commons


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
        dragon_deer = r"""hmm.. nah. have another deer.
       ""\/ \/""
         "\__/"
          (oo)
 -. ______-LJ
  ,'        |
  |.____..  /
  \\      /A\
  |A      |//"""
        dragon_one = r"""                     _ _
              _     //` `\
          _,-"\%   // /``\`\
     ~^~ >__^  |% // /  } `\`\
            )  )%// / }  } }`\`\
           /  (%/'/.\_/\_/\_/\`/
          (    '         `-._`
           \   ,     (  \   _`-.__.-;%>
          /_`\ \      `\ \." `-..-'`
         ``` /_/`"-=-'`/_/
    jgs     ```       ```"""
        dragon_two = r"""           ____ __
          { --.\  |          .)%%%)%%
           '-._\\ | (\___   %)%%(%%(%%%
               `\\|{/ ^ _)-%(%%%%)%%;%%%
           .'^^^^^^^  /`    %%)%%%%)%%%'
  jgs     //\   ) ,  /       '%%%%(%%'
    ,  _.'/  `\<-- \<
     `^^^`     ^^   ^^"""
        rand = Commons.get_random_int(0, 100)[0]
        if rand == 15:
            dragon = dragon_deer
        elif rand % 2 == 0:
            dragon = dragon_one
        else:
            dragon = dragon_two
        return event.create_response(dragon)

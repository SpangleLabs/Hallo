from hallo.function import Function


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
        return event.create_response(train)

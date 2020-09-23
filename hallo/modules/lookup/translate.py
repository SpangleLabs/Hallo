import urllib.parse

from hallo.function import Function
from hallo.inc.commons import Commons


class Translate(Function):
    """
    Uses google translate to translate a phrase to english, or to any specified language
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "translate"
        # Names which can be used to address the function
        self.names = {"translate"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Translates a given block of text. Format: translate <from>-><to> <text>"
        )

    def run(self, event):
        if len(event.command_args.split()) <= 1:
            lang_change = ""
            trans_string = event.command_args
        else:
            lang_change = event.command_args.split()[0]
            trans_string = " ".join(event.command_args.split()[1:])
        if "->" not in lang_change:
            lang_from = "auto"
            lang_to = "en"
            trans_string = lang_change + " " + trans_string
        else:
            lang_from = lang_change.split("->")[0]
            lang_to = lang_change.split("->")[1]
        trans_safe = urllib.parse.quote(trans_string.strip(), "")
        # This uses google's secret translate API, it's not meant to be used by robots, and often it won't work
        url = (
            "http://translate.google.com/translate_a/t?client=t&text={}&hl=en&sl={}&tl={}"
            "&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1".format(
                trans_safe, lang_from, lang_to
            )
        )
        trans_dict = Commons.load_url_json(url, [], True)
        translation_string = " ".join([x[0] for x in trans_dict[0]])
        return event.create_response("Translation: {}".format(translation_string))
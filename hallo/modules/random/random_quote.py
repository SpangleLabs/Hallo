from hallo.function import Function
from hallo.inc.commons import Commons


class RandomQuote(Function):
    """
    Returns a random quote
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random quote"
        # Names which can be used to address the function
        self.names = {"random quote", "randomquote", "quote"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a quote. Format: random quote"

    def run(self, event):
        url = "https://type.fit/api/quotes"
        # Get api response
        json_dict = Commons.load_url_json(url)
        # Select a random quote from response
        quote = Commons.get_random_choice(json_dict)[0]
        # Construct response
        quote_text = quote["text"]
        author = quote["author"]
        output = '"{}" - {}'.format(quote_text, author)
        return event.create_response(output)
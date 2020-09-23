import re

from hallo.function import Function
from hallo.inc.commons import Commons


class Wiki(Function):
    """
    Lookup wiki article and return the first paragraph or so.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "wiki"
        # Names which can be used to address the function
        self.names = {"wiki", "wikipedia"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Reads the first paragraph from a wikipedia article"

    def run(self, event):
        line_clean = event.command_args.strip().replace(" ", "_")
        url = (
            "https://en.wikipedia.org/w/api.php?format=json&action=query&titles={}"
            "&prop=revisions&rvprop=content&redirects=True".format(line_clean)
        )
        article_dict = Commons.load_url_json(url)
        page_code = list(article_dict["query"]["pages"])[0]
        article_text = article_dict["query"]["pages"][page_code]["revisions"][0]["*"]
        old_scan = article_text
        new_scan = re.sub("{{[^{^}]*}}", "", old_scan)  # Strip templates
        while new_scan != old_scan:
            old_scan = new_scan
            new_scan = re.sub(
                "{{[^{^}]*}}", "", old_scan
            )  # Keep stripping templates until they're gone
        plain_text = new_scan.replace("''", "")
        plain_text = re.sub(r"<ref[^<]*</ref>", "", plain_text)  # Strip out references
        old_scan = plain_text
        # Repeatedly strip links from image descriptions
        new_scan = re.sub(r"(\[\[File:[^\][]+)\[\[[^\]]+]]", r"\1", old_scan)
        while new_scan != old_scan:
            old_scan = new_scan
            new_scan = re.sub(r"(\[\[File:[^\][]+)\[\[[^\]]+]]", r"\1", old_scan)
        plain_text = new_scan
        plain_text = re.sub(r"\[\[File:[^\]]+]]", "", plain_text)  # Strip out images
        plain_text = re.sub(
            r"\[\[[^\]^|]*\|([^\]]*)]]", r"\1", plain_text
        )  # Strip out links with specified names
        plain_text = re.sub(r"\[\[([^\]]*)]]", r"\1", plain_text)  # Strip out links
        plain_text = re.sub(r"<!--[^>]*-->", "", plain_text)  # Strip out comments
        plain_text = re.sub(
            r"<ref[^>]*/>", "", plain_text
        )  # Strip out remaining references
        first_paragraph = plain_text.strip().split("\n")[0]
        return event.create_response(first_paragraph)
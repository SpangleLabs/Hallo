import logging
import time
from xml.dom import minidom

from hallo.events import EventHour
from hallo.function import Function
from hallo.inc.commons import Commons

logger = logging.getLogger(__name__)


class UpdateCurrencies(Function):
    """
    Updates all currencies in the ConvertRepo
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "update currencies"
        # Names which can be used to address the Function
        self.names = {
            "update currencies",
            "convert update currencies",
            "currency update",
            "update currency",
            "currencies update",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Update currency conversion figures, using data from the money converter, the European "
            "central bank, forex and preev."
        )

    def run(self, event):
        # Get convert repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Update all sources
        output_lines = self.update_all(repo)
        # Return output
        return event.create_response("\n".join(output_lines))

    def get_passive_events(self):
        return {EventHour}

    def passive_run(self, event, hallo_obj):
        # Get convert repo
        function_dispatcher = hallo_obj.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Update all sources
        output_lines = self.update_all(repo)
        for line in output_lines:
            logger.info(line)
        return None

    def update_all(self, repo):
        output_lines = []
        # Update with the European Bank
        try:
            output_lines.append(
                self.update_from_european_bank_data(repo)
                or "Updated currency data from the European Central Bank."
            )
        except Exception as e:
            output_lines.append(
                "Failed to update European Central Bank data. {}".format(e)
            )
        # Update with Forex
        try:
            output_lines.append(
                self.update_from_forex_data(repo) or "Updated currency data from Forex."
            )
        except Exception as e:
            output_lines.append("Failed to update Forex data. {}".format(e))
        # Update with Preev
        try:
            output_lines.append(
                self.update_from_cryptonator_data(repo)
                or "Updated currency data from Cryptonator."
            )
        except Exception as e:
            output_lines.append("Failed to update Cryptonator data. {}".format(e))
        # Save repo
        repo.save_json()
        return output_lines

    def update_from_european_bank_data(self, repo):
        """
        Updates the value of conversion currency units using The European Bank data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from european bank website
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        xml_string = Commons.load_url_string(url)
        # Parse data
        doc = minidom.parseString(xml_string)
        root = doc.getElementsByTagName("gesmes:Envelope")[0]
        cube_one_elem = root.getElementsByTagName("Cube")[0]
        cube_two_elem = cube_one_elem.getElementsByTagName("Cube")[0]
        for cube_three_elem in cube_two_elem.getElementsByTagName("Cube"):
            # Get currency code from currency Attribute
            currency_code = cube_three_elem.getAttributeNode("currency").nodeValue
            # Get value from rate attribute and get reciprocal.
            currency_value = 1 / float(
                cube_three_elem.getAttributeNode("rate").nodeValue
            )
            # Get currency unit
            currency_unit = currency_type.get_unit_by_name(currency_code)
            # If unrecognised currency, SKIP
            if currency_unit is None:
                continue
            # Set Value
            currency_unit.update_value(currency_value)

    def update_from_forex_data(self, repo):
        """
        Updates the value of conversion currency units using Forex data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from forex website
        url = "https://rates.fxcm.com/RatesXML3"
        xml_string = Commons.load_url_string(url)
        # Parse data
        doc = minidom.parseString(xml_string)
        rates_elem = doc.getElementsByTagName("Rates")[0]
        for rate_elem in rates_elem.getElementsByTagName("Rate"):
            # Get data from element
            symbol_data = rate_elem.getElementsByTagName("Symbol")[0].firstChild.data
            if not symbol_data.startswith("EUR"):
                continue
            bid_data = float(rate_elem.getElementsByTagName("Bid")[0].firstChild.data)
            ask_data = float(rate_elem.getElementsByTagName("Ask")[0].firstChild.data)
            # Get currency code and value from data
            currency_code = symbol_data[3:]
            currency_value = 1 / (0.5 * (bid_data + ask_data))
            # Get currency unit
            currency_unit = currency_type.get_unit_by_name(currency_code)
            # If unrecognised code, skip
            if currency_unit is None:
                continue
            # Set Value
            currency_unit.update_value(currency_value)

    def update_from_cryptonator_data(self, repo):
        """
        Updates the value of conversion cryptocurrencies using cryptonator data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull json data from preev website, combine into 1 dict
        currency_codes = ["LTC", "BTC", "BCH", "DOGE", "XMR", "ETH", "ETC", "DASH"]
        for code in currency_codes:
            # Get data
            try:
                data = Commons.load_url_json(
                    "https://api.cryptonator.com/api/ticker/{}-eur".format(code)
                )
            except Exception as e:
                # If it fails, because it failed to parse the JSON, give it another go
                # Cryptonator API returns HTML sometimes. I don't know why.
                if "Expecting value:" in str(e):
                    time.sleep(5)
                    data = Commons.load_url_json(
                        "https://api.cryptonator.com/api/ticker/{}-eur".format(code)
                    )
                else:
                    raise e
            # Get the ConvertUnit object for the currency reference
            currency_unit = currency_type.get_unit_by_name(code)
            if currency_unit is None:
                continue
            # Update the value
            currency_unit.update_value(data["ticker"]["price"])
from hallo.function import Function
from hallo.inc.commons import Commons


class RandomPerson(Function):
    """
    Returns a randomly generated person
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random person"
        # Names which can be used to address the function
        self.names = {
            "random person",
            "randomperson",
            "generate person",
            "generate user",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            'Generates and returns a random person\'s details. Specify "full" for more details. '
            "Format: random person"
        )

    def run(self, event):
        input_clean = event.command_args.strip().lower()
        url = "https://api.randomuser.me/0.6/?nat=gb&format=json"
        # Get api response
        json_dict = Commons.load_url_json(url)
        user_dict = json_dict["results"][0]["user"]
        # Construct response
        name = "{} {} {}".format(
            user_dict["name"]["title"],
            user_dict["name"]["first"],
            user_dict["name"]["last"],
        ).title()
        email = user_dict["email"]
        address = "{}, {}, {}".format(
            user_dict["location"]["street"].title(),
            user_dict["location"]["city"].title(),
            user_dict["location"]["postcode"],
        )
        username = user_dict["username"]
        password = user_dict["password"]
        date_of_birth = Commons.format_unix_time(int(user_dict["dob"]))
        phone_home = user_dict["phone"]
        phone_mob = user_dict["cell"]
        national_insurance = user_dict["NINO"]
        pronoun = "he" if user_dict["gender"] == "male" else "she"
        pronoun_possessive = "his" if user_dict["gender"] == "male" else "her"
        if input_clean not in ["more", "full", "verbose", "all"]:
            output = "I have generated this person: Say hello to {}. {} was born at {}.".format(
                name, pronoun.title(), date_of_birth
            )
            return event.create_response(output)
        output = (
            "I have generated this person: Say hello to {}. "
            "{} was born at {} and lives at {}. "
            '{} uses the email {}, the username {} and usually uses the password "{}". '
            "{} home number is {} but {} mobile number is {}. "
            "{} national insurance number is {}.".format(
                name,
                pronoun.title(),
                date_of_birth,
                address,
                pronoun.title(),
                email,
                username,
                password,
                pronoun_possessive.title(),
                phone_home,
                pronoun_possessive,
                phone_mob,
                pronoun_possessive.title(),
                national_insurance,
            )
        )
        return event.create_response(output)

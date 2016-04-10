from Function import Function
from inc.commons import Commons
import math


class Hailstone(Function):
    """
    Runs a collatz (or hailstone) function on a specified number, returning the sequence generated.
    """
    LIMIT = 1000

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "hailstone"
        # Names which can be used to address the Function
        self.names = {"hailstone", "collatz", "collatz sequence"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "The hailstone function has to be given with a number (to generate the collatz sequence of.)"

    def run(self, line, user_obj, destination_obj=None):
        """Returns the hailstone sequence for a given number. Format: hailstone <number>"""
        line_clean = line.strip().lower()
        if not line_clean.isdigit():
            return "Error, the hailstone function has to be given with a number (to generate the collatz sequence of.)"
        number = int(line_clean)
        if number > Hailstone.LIMIT:
            return "Error, this is above the limit for this function."
        sequence = self.collatz_sequence([number])
        output_string = "Hailstone (Collatz) sequence for " + str(number) + ": "
        output_string += '->'.join(str(x) for x in sequence) + " (" + str(len(sequence)) + " steps.)"
        return output_string

    def collatz_sequence(self, sequence):
        num = int(sequence[-1])
        if num == 1:
            return sequence
        elif num % 2 == 0:
            sequence.append(num // 2)
            return self.collatz_sequence(sequence)
        else:
            sequence.append(3 * num + 1)
            return self.collatz_sequence(sequence)


class NumberWord(Function):
    """
    Converts a number to the textual representation of that number.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "number"
        # Names which can be used to address the Function
        self.names = {"number", "number word", "numberword"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the textual representation of a given number. Format: number <number>"

    def run(self, line, user_obj, destination_obj=None):
        if line.count(' ') == 0:
            number = line
            lang = "american"
        elif line.split()[1].lower() in ["british", "english"]:
            number = line.split()[0]
            lang = "english"
        elif line.split()[1].lower() in ["european", "french"]:
            number = line.split()[0]
            lang = "european"
        else:
            number = line.split()[0]
            lang = "american"
        if Commons.check_numbers(number):
            number = number
        elif Commons.check_calculation(number):
            function_dispatcher = user_obj.server.hallo.function_dispatcher
            calc_func = function_dispatcher.get_function_by_name("calc")
            calc_obj = function_dispatcher.get_function_object(calc_func)
            number = calc_obj.process_calculation(number)
        else:
            return "You must enter a valid number or calculation."
        return self.number_word(number, lang) + "."

    def number_word(self, number, lang="american"):
        # Set up some arrays
        digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
                  'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['zero', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        normal_segs = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion',
                       'septillion', 'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion',
                       'tredecillion']
        european_segs = ['', 'thousand', 'million', 'milliard', 'billion', 'billiard', 'trillion', 'trilliard',
                         'quadrillion', 'quadrilliard', 'quintillion', 'quintilliard', 'sextillion', 'sextilliard',
                         'septillion']
        english_segs = ['', 'thousand', 'million', 'thousand million', 'billion', 'thousand billion', 'trillion',
                        'thousand trillion', 'quadrillion', 'thousand quadrillion', 'quintillion',
                        'thousand quintillion', 'sextillion', 'thousand sextillion', 'septillion']
        # Check for amount of decimal points
        if number.count('.') > 1:
            return "There's too many decimal points in that."
        # If there's a decimal point, write decimal parts
        elif number.count('.') == 1:
            exp_number = number.split('.')
            number_decimal = exp_number[1]
            number = exp_number[0]
            decimal = " point"
            for num in number_decimal:
                decimal = decimal + " " + digits[int(num)]
        else:
            decimal = ""
        # Convert number to a string, to string
        number = str(number)
        # Check if number is negative
        if number[0] == "-":
            number = number[1:]
            string = 'negative '
        else:
            string = ''
        # find number of segments, and justify up to a number of digits divisible by 3
        segments = int(math.ceil(float(len(number)) / 3) + 0.01)
        number = number.rjust(3 * segments, '0')
        # If number is zero, say zero.
        if number == "000":
            string += "zero"
        # Write out segments
        for seg in range(segments):
            start = seg * 3
            end = start + 3
            segment = number[start:end]
            # string = string + "(" + segment + ")"
            # Convert first number of segment
            if segment[0] != "0":
                string = string + digits[int(segment[0])] + " hundred "
                if int(segment[1:]) != 0:
                    string += "and "
            elif seg != 0 and int(segment[1:]) != 0:
                string += "and "
            # Convert second and third numbers of segment
            if int(segment[1:]) == 0:
                pass
            elif int(segment[1:]) < 20:
                string = string + digits[int(segment[1:])]
            else:
                string += tens[int(segment[1])]
                if segment[2] != "0":
                    string = string + "-" + digits[int(segment[2])]
            # Add segment cardinal.
            if seg != (segments - 1) and segment != "000":
                if lang.lower() == "american":
                    string = string + " " + normal_segs[segments - seg - 1]
                elif lang.lower() == "english":
                    string = string + " " + english_segs[segments - seg - 1]
                elif lang.lower() == "european":
                    string = string + " " + european_segs[segments - seg - 1]
                else:
                    string = string + " " + normal_segs[segments - seg - 1]
            if seg != (segments - 1) and int(number[end:end + 3]) != 0:
                string += ', '
        # Put string together and output
        string += decimal
        return string


class PrimeFactors(Function):
    """
    Finds prime factors of a specified number
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "prime factors"
        # Names which can be used to address the Function
        self.names = {"prime factors", "prime factor", "primefactors", "primefactor"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the prime factors of a given number. Format: prime factors <number>"

    def run(self, line, user_obj, destination_obj=None):
        line_clean = line.strip().lower()
        if line_clean.isdigit():
            number = int(line_clean)
        elif Commons.check_calculation(line_clean):
            function_dispatcher = user_obj.server.hallo.function_dispatcher
            calc_func = function_dispatcher.get_function_by_name("calc")
            calc_obj = function_dispatcher.get_function_object(calc_func)
            number_str = calc_obj.process_calculation(line_clean)
            if "." in number_str:
                return "This calculation does not result in an integer. The answer is: " + number_str
            number = int(number_str)
        else:
            return "This is not a valid number or calculation."
        prime_factors = self.find_prime_factors(number)
        return "The prime factors of " + str(number) + " are: " + 'x'.join(str(x) for x in prime_factors) + "."

    def find_prime_factors(self, number):
        number = int(number)
        factors = []
        not_prime = False
        for x in range(2, int(math.sqrt(number)) + 1):
            if number % x == 0:
                factors.append(x)
                factors.extend(self.find_prime_factors(number // x))
                not_prime = True
                break
        if not not_prime:
            return [number]
        else:
            return factors


class ChangeOptions(Function):
    """
    Returns the number of options for change in UK currency for a certain value
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "change options"
        # Names which can be used to address the Function
        self.names = {"change options", "changeoptions", "change", "change ways"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the different ways to give change for a given amount (in pence, using british " \
                         "coins.) Format: change_options <number>"

    def run(self, line, user_obj, destination_obj=None):
        """
        Returns the number of ways to give change for a given amount (in pence, using british coins.)
        Format: change_options <number>
        """
        line_clean = line.strip().lower()
        try:
            number = int(line_clean)
        except ValueError:
            return "Error, That's not a valid integer."
        if number <= 0:
            return "Error, input must be a positive integer."
        if number > 20:
            return "Error, for reasons of output length, I can't return change options for more than 20 pence."
        coins = [200, 100, 50, 20, 10, 5, 2, 1]
        options = self.change_options(coins, 0, number)
        output_string = 'Possible ways to give that change: '
        for option in options:
            output_string += '[' + ','.join(str(x) for x in option) + '],'
        return output_string + "."

    def change_options(self, coins, coin_num, amount):
        coin_amount = amount // coins[coin_num]
        change = []
        if amount == 0:
            return change
        elif coin_num == len(coins) - 1:
            change.append([coins[coin_num]] * (amount // coins[coin_num]))
        else:
            for x in range(coin_amount, -1, -1):
                remaining = amount - x * coins[coin_num]
                if remaining == 0:
                    change.append(x * [coins[coin_num]])
                else:
                    change_add = self.change_options(coins, coin_num + 1, remaining)
                    for change_option in change_add:
                        change.append(x * [coins[coin_num]] + change_option)
        return change


class Average(Function):
    """
    Finds the average of a given list of numbers.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "average"
        # Names which can be used to address the Function
        self.names = {"average", "avg", "mean"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Finds the average of a list of numbers. Format: average <number1> <number2> ... <number n>"

    def run(self, line, user_obj, destination_obj=None):
        number_list = line.split()
        try:
            number_sum = sum(float(x) for x in number_list)
        except ValueError:
            return "Error, Please only input a list of numbers"
        return "The average of " + ', '.join(number_list) + " is: " + str(number_sum / float(len(number_list))) + "."


class HighestCommonFactor(Function):
    """
    Finds the highest common factor of a pair of numbers.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "highest common factor"
        # Names which can be used to address the Function
        self.names = {"highest common factor", "highestcommonfactor", "hcf"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the highest common factor of two numbers. " \
                         "Format: highest common factor <number1> <number2>"

    def run(self, line, user_obj, destination_obj=None):
        # Getting function_dispatcher and required function objects
        hallo_obj = user_obj.get_server().get_hallo()
        function_dispatcher = hallo_obj.get_function_dispatcher()
        prime_factors_class = function_dispatcher.get_function_by_name("prime factors")
        euler_class = function_dispatcher.get_function_by_name("euler")
        prime_factors_obj = function_dispatcher.get_function_object(prime_factors_class)
        eurler_obj = function_dispatcher.get_function_object(euler_class)
        # Preflight checks
        if len(line.split()) != 2:
            return "You must provide two arguments."
        input_one = line.split()[0]
        input_two = line.split()[1]
        try:
            number_one = int(input_one)
            number_two = int(input_two)
        except ValueError:
            return "Both arguments must be integers."
        # Get prime factors of each, get intersection, then product of that.
        number_one_factors = prime_factors_obj.find_prime_factors(number_one)
        number_two_factors = prime_factors_obj.find_prime_factors(number_two)
        common_factors = eurler_obj.list_intersection(number_one_factors, number_two_factors)
        hcf = eurler_obj.list_product(common_factors)
        return "The highest common factor of " + str(number_one) + " and " + str(number_two) + " is " + str(hcf) + "."


class SimplifyFraction(Function):
    """
    Simplifies an inputted fraction
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "simplify fraction"
        # Names which can be used to address the Function
        self.names = {"simplify fraction", "simplifyfraction", "fraction", "simple fraction", "base fraction",
                      "fraction simplify"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a fraction in its simplest form. Format: simplify fraction <numerator>/<denominator>"

    def run(self, line, user_obj, destination_obj=None):
        # Getting function_dispatcher and required function objects
        hallo_obj = user_obj.get_server().get_hallo()
        function_dispatcher = hallo_obj.get_function_dispatcher()
        prime_factors_class = function_dispatcher.get_function_by_name("prime factors")
        euler_class = function_dispatcher.get_function_by_name("euler")
        prime_factors_obj = function_dispatcher.get_function_object(prime_factors_class)
        euler_obj = function_dispatcher.get_function_object(euler_class)
        # preflight checks
        if line.count("/") != 1:
            return "Please give input in the form: <numerator>/<denominator>"
        # Get numerator and denominator
        numerator_string = line.split('/')[0]
        denominator_string = line.split('/')[1]
        try:
            numerator = int(numerator_string)
            denominator = int(denominator_string)
        except ValueError:
            return "Numerator and denominator must be integers."
        # Sort all this and get the value
        numerator_factors = prime_factors_obj.find_prime_factors(numerator)
        denominator_factors = prime_factors_obj.find_prime_factors(denominator)
        numerator_factors_new = euler_obj.list_minus(numerator_factors,
                                                     euler_obj.list_intersection(denominator_factors,
                                                                                 numerator_factors))
        denominator_factors_new = euler_obj.list_minus(denominator_factors,
                                                       euler_obj.list_intersection(denominator_factors,
                                                                                   numerator_factors))
        numerator_new = euler_obj.list_product(numerator_factors_new)
        denominator_new = euler_obj.list_product(denominator_factors_new)
        return str(numerator) + "/" + str(denominator) + " = " + str(numerator_new) + "/" + str(denominator_new) + "."


class Calculate(Function):
    """
    Standard calculator function
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "calc"
        # Names which can be used to address the Function
        self.names = {"calc", "calculate", "calculator"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Calculate function, calculates the answer to mathematical expressions. " \
                         "Format: calc <calculation>"

    def run(self, line, user_obj, destination_obj=None):
        calc = line
        # check for equals signs, and split at them if so.
        if calc.count('=') >= 1:
            calc_parts = calc.split('=')
            ans_parts = []
            number_answers = []
            num_calcs = 0
            for calc_part in calc_parts:
                # run preflight checks, if it passes do the calculation, if it doesn't return the same text.
                try:
                    self.preflight_checks(calc_part)
                    calc_part = calc_part.replace(' ', '').lower()
                    ans_part = self.process_calculation(calc_part)
                    ans_parts.append(ans_part)
                    number_answers.append(ans_part)
                    num_calcs += 1
                except Exception as e:
                    print(str(e))
                    ans_parts.append(calc_part)
            answer = '='.join(ans_parts)
            # Check if all number results are equal.
            if not number_answers or number_answers.count(number_answers[0]) == len(number_answers):
                answer += "\n" + "Wait, that's not right..."
            return answer
        # If there's no equals signs, collapse it all together
        calc = calc.replace(' ', '').lower()
        try:
            self.preflight_checks(calc)
            answer = self.process_calculation(calc)
        except Exception as e:
            answer = str(e)
        return answer

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        # Check if fullLine is a calculation, and is not just numbers, and contains numbers.
        if not Commons.check_calculation(full_line):
            return None
        if Commons.check_numbers(full_line.replace(".", "")):
            return None
        if not any([char in full_line for char in [str(x) for x in range(10)] + ["e", "pi"]]):
            return None
        # Clean up the line and feed to the calculator.
        calc = full_line.replace(' ', '').lower()
        try:
            self.preflight_checks(calc)
            answer = self.process_calculation(calc)
            return answer
        except Exception as e:
            print("Passive calc failed: "+str(e))
            return None

    def after_infix(self, calc, sub_str):
        # If substring is at the end, return empty string.
        if calc.endswith(sub_str):
            return ""
        # Find position and get the calculation after that position.
        pos = calc.find(str(sub_str))
        post_calc = calc[pos + len(sub_str):]
        # Check each substring of post_calc for whether it's a valid float, starting from longest.
        for sub_post_calc in [post_calc[:len(post_calc) - x] for x in range(len(post_calc))]:
            try:
                float(sub_post_calc)
                return sub_post_calc
            except ValueError:
                pass
        return ""

    def before_infix(self, calc, sub_str):
        # If substring is at the start, return empty string.
        if calc.startswith(sub_str):
            return ""
        # Find position and get the calculation before that position.
        pos = calc.find(str(sub_str))
        pre_calc = calc[:pos]
        # Check each substring of pre_calc for whether it's a valid float, starting from longest.
        for sub_pre_calc in [pre_calc[x:] for x in range(len(pre_calc))]:
            try:
                float(sub_pre_calc)
                if sub_pre_calc[0] == "+":
                    sub_pre_calc = sub_pre_calc[1:]
                return sub_pre_calc
            except ValueError:
                pass
        return ""

    def preflight_checks(self, calc):
        # strip spaces
        calc_clean = calc.replace(' ', '').lower()
        # make sure only legit characters are allowed
        if not Commons.check_calculation(calc_clean):
            # TODO use custom exception
            raise Exception('Error, Invalid characters in expression')
        # make sure open brackets don't out-number close
        if calc.count('(') > calc.count(')'):
            raise Exception('Error, too many open brackets')
        # Make sure close brackets don't out-number open.
        # Previously I thought it would be okay to skip this, but "(21/3))+2))*5" evaluates as 17, rather than 45
        if calc.count(')') > calc.count('('):
            raise Exception('Error, too many close brackets')
        if len(calc) == 0:
            raise Exception("Error, empty calculation or brackets")
        return True

    def process_trigonometry(self, calc, running_calc):
        temp_answer = self.process_calculation(running_calc)
        running_calc = '(' + running_calc + ')'
        before = calc.split(running_calc)[0]
        trig_dict = {'acos': math.acos, 'asin': math.asin, 'atan': math.atan, 'cos': math.cos, 'sin': math.sin,
                     'tan': math.tan, 'sqrt': math.sqrt, 'log': math.log, 'acosh': math.acosh, 'asinh': math.asinh,
                     'atanh': math.atanh, 'cosh': math.cosh, 'sinh': math.sinh, 'tanh': math.tanh, 'gamma': math.gamma}
        max_len = 0
        max_name = ""
        for trig_name in trig_dict:
            if before[-len(trig_name):] == trig_name:
                if len(trig_name) > max_len:
                    max_len = len(trig_name)
                    max_name = trig_name
        if max_len > 0:
            return [max_name + running_calc, trig_dict[max_name](float(temp_answer))]
        return [running_calc, temp_answer]

    def process_calculation(self, calc):
        # Swapping "x" for "*"
        calc = calc.replace("x", "*")
        # constant evaluation
        while calc.count('pi') != 0:
            temp_answer = math.pi
            if self.before_infix(calc, 'pi') != '':
                temp_answer = '*' + str(temp_answer)
            if self.after_infix(calc, 'pi') != '':
                temp_answer = str(temp_answer) + '*'
            calc = calc.replace('pi', str(temp_answer))
            del temp_answer
        while calc.count('e') != 0:
            temp_answer = math.e
            if self.before_infix(calc, 'e') != '':
                temp_answer = '*' + str(temp_answer)
            if self.after_infix(calc, 'e') != '':
                temp_answer = str(temp_answer) + '*'
            calc = calc.replace('e', str(temp_answer))
            del temp_answer
        # bracket processing
        if calc.count(")-") != 0:
            calc = calc.replace(")-", ")+-")
        while calc.count('(') != 0:
            temp_calc = calc[calc.find('(') + 1:]
            bracket = 1
            running_calc = ''
            # Loop through the string
            next_char = None
            for next_char in temp_calc:
                if next_char == '(':
                    bracket += 1
                elif next_char == ')':
                    bracket -= 1
                if bracket == 0:
                    if len(running_calc) == 0:
                        raise Exception("Error, empty calculation or brackets")
                    # tempans = mod_calc.fnn_calc_process(self,running_calc)
                    # running_calc = '('+running_calc+')'
                    trig_check = self.process_trigonometry(calc, running_calc)
                    temp_answer = trig_check[1]
                    running_calc = trig_check[0]
                    before_running_calc = self.before_infix(calc, running_calc)
                    if before_running_calc != '':
                        running_calc = before_running_calc + running_calc
                        temp_answer = before_running_calc + '*' + str(temp_answer)
                    after_running_calc = self.after_infix(calc, running_calc)
                    if after_running_calc != '' and after_running_calc[0] != '+':
                        running_calc = running_calc + after_running_calc
                        temp_answer = str(temp_answer) + '*' + after_running_calc
                    calc = calc.replace(running_calc, str(temp_answer))
                    del temp_answer
                    break
                running_calc = running_calc + next_char
            del temp_calc, bracket, running_calc, next_char
        calc = calc.replace(')', '')
        # powers processing
        while calc.count('^') != 0:
            pre_calc = self.before_infix(calc, '^')
            post_calc = self.after_infix(calc, '^')
            calc = calc.replace(str(pre_calc) + '^' + str(post_calc), str(float(pre_calc) ** float(post_calc)), 1)
            del pre_calc, post_calc
        # powers processing 2
        while calc.count('**') != 0:
            pre_calc = self.before_infix(calc, '**')
            post_calc = self.after_infix(calc, '**')
            calc = calc.replace(str(pre_calc) + '**' + str(post_calc), str(float(pre_calc) ** float(post_calc)), 1)
            del pre_calc, post_calc
        # modulo processing
        while calc.count('%') != 0:
            pre_calc = self.before_infix(calc, '%')
            post_calc = self.after_infix(calc, '%')
            if float(post_calc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(pre_calc) + '%' + str(post_calc), str(float(pre_calc) % float(post_calc)), 1)
            del pre_calc, post_calc
        # multiplication processing
        while calc.count('/') != 0:
            pre_calc = self.before_infix(calc, '/')
            post_calc = self.after_infix(calc, '/')
            if float(post_calc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(pre_calc) + '/' + str(post_calc), str(float(pre_calc) / float(post_calc)), 1)
            del pre_calc, post_calc
        # multiplication processing
        while calc.count('*') != 0:
            pre_calc = self.before_infix(calc, '*')
            post_calc = self.after_infix(calc, '*')
            calc = calc.replace(str(pre_calc) + '*' + str(post_calc), str(float(pre_calc) * float(post_calc)), 1)
            del pre_calc, post_calc
        # addition processing
        calc = calc.replace('-', '+-')
        answer = 0
        calc = calc.replace('e+', 'e')
        for temp_answer in calc.split('+'):
            if temp_answer != '':
                try:
                    answer += float(temp_answer)
                except ValueError:
                    answer = answer
        answer = '{0:.10f}'.format(answer)
        if '.' in answer:
            while answer[-1] == '0':
                answer = answer[:-1]
        if answer[-1] == '.':
            answer = answer[:-1]
        return answer

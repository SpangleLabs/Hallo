from Function import Function
import math
import itertools
from modules.Games import Deck, Hand  # Problem 54 is based on poker.
from modules.Math import ChangeOptions, NumberWord, PrimeFactors, SimplifyFraction


class Euler(Function):
    """
    euler project functions
    """

    mHalloObject = None  # Todo: Rename and type hint.

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "euler"
        # Names which can be used to address the Function
        self.names = {"euler", "euler project", "project euler"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Project Euler functions. Format: \"euler list\" to list project euler solutions. " \
                         "\"euler <number>\" for the solution to project euler problem of the given number."

    def run(self, event):
        # Some functions might need this.
        self.mHalloObject = event.server.hallo
        line_clean = event.command_args.strip().lower()
        if line_clean == "list":
            return self.list_all()
        elif line_clean.isdigit():
            return self.run_function(line_clean)
        else:
            count_solutions = len(
                [func_name for func_name in dir(self) if func_name[:5] == 'euler' and func_name[5:].isdigit()])
            output_string = "I'm learning to complete the project Euler programming problems. " \
                            "I've not done many so far, I've only done {} of the 514 problems. ".format(count_solutions)
            output_string += "But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, " \
                             "say 'Hallo Euler {num}' for the answer to challenge number {num}."
            return output_string

    def list_all(self):
        # list all available project Euler answers
        problem_func_names = []
        for func_name in dir(self):
            if func_name[:5] == 'euler' and func_name[5:].isdigit():
                problem_func_names.append(func_name[5:])
        problem_func_names = sorted(problem_func_names, key=int)
        output_string = "Currently I can do {} Project Euler problems ".format(len(problem_func_names))
        output_string += ', '.join(problem_func_names[:-1])
        output_string += " and " + problem_func_names[-1] + "."
        return output_string

    def run_function(self, number_string):
        function_name = "euler" + number_string
        function_names = [func_name for func_name in dir(self) if func_name[:5] == 'euler' and func_name[5:].isdigit()]
        if function_name not in function_names:
            return "Error, I don't think I've solved that one yet."
        function_obj = getattr(self, function_name)
        if not hasattr(function_obj, "__call__"):
            return "Error, That doesn't seem to work."
        try:
            output_string = "Euler project problem {}? I think the answer is: {}.".format(number_string, function_obj())
        except Exception as e:
            output_string = "Hmm, seems that one has an error... darnit."
            print("EULER ERROR: {}".format(e))
        return output_string

    def check_prime(self, input_number):
        check_prime = input_number
        if check_prime <= 1:
            return False
        for j in range(2, int(math.floor(math.sqrt(check_prime))) + 1):
            if check_prime % j == 0:
                return False
        return True

    def check_palindrome(self, input_string):
        if input_string == input_string[::-1]:
            return True
        else:
            return False

    def check_list_in_list(self, list_small, list_big):
        list_test = list(list_big)
        for x in list_small:
            if x in list_test:
                list_test.remove(x)
            else:
                return False
        return True

    def check_concat_primes(self, number_one, number_two):
        check_one = self.check_prime(int(str(number_one) + str(number_two)))
        if not check_one:
            return False
        check_two = self.check_prime(int(str(number_two) + str(number_one)))
        if not check_two:
            return False
        return True

    def find_number_of_factors(self, number):
        number = int(number)
        num_factors = 2
        for x in range(2, int(math.sqrt(number)) + 1):
            if number % x == 0:
                num_factors += 2
        return num_factors

    def find_factors(self, number):
        number = int(number)
        factors = []
        for x in range(1, int(math.sqrt(number)) + 1):
            if number % x == 0:
                factors.append(x)
                if number / x != x:
                    factors.append(number / x)
        return factors

    def find_word_value(self, word):
        value = 0
        word = word.upper()
        for char in word:
            value += ord(char) - 64
        return value

    def remove_list_items(self, input_list, remove_item):
        new_list = []
        for item in input_list:
            if item != remove_item:
                new_list.append(item)
        return new_list

    def get_list_pandigitals(self):
        pandigitals = []
        digits = list(range(10))
        for a in range(9):
            adigit = digits[a + 1]
            adigits = list(digits)
            del adigits[a + 1]
            for b in range(9):
                bdigit = adigits[b]
                bdigits = list(adigits)
                del bdigits[b]
                for c in range(8):
                    cdigit = bdigits[c]
                    cdigits = list(bdigits)
                    del cdigits[c]
                    for d in range(7):
                        ddigit = cdigits[d]
                        ddigits = list(cdigits)
                        del ddigits[d]
                        for e in range(6):
                            edigit = ddigits[e]
                            edigits = list(ddigits)
                            del edigits[e]
                            for f in range(5):
                                fdigit = edigits[f]
                                fdigits = list(edigits)
                                del fdigits[f]
                                for g in range(4):
                                    gdigit = fdigits[g]
                                    gdigits = list(fdigits)
                                    del gdigits[g]
                                    for h in range(3):
                                        hdigit = gdigits[h]
                                        hdigits = list(gdigits)
                                        del hdigits[h]
                                        for i in range(2):
                                            idigit = hdigits[i]
                                            idigits = list(hdigits)
                                            del idigits[i]
                                            jdigit = idigits[0]
                                            pandigitals.append(
                                                1000000000 * adigit +
                                                100000000 * bdigit +
                                                10000000 * cdigit +
                                                1000000 * ddigit +
                                                100000 * edigit +
                                                10000 * fdigit +
                                                1000 * gdigit +
                                                100 * hdigit +
                                                10 * idigit +
                                                jdigit)
        return pandigitals

    def euler1(self):
        three_count = math.floor(999 / 3)
        five_count = math.floor(999 / 5)
        fifteen_count = math.floor(999 / 15)
        three_sum = 3 * ((0.5 * (three_count ** 2)) + (0.5 * three_count))
        five_sum = 5 * ((0.5 * (five_count ** 2)) + (0.5 * five_count))
        fifteen_sum = 15 * ((0.5 * (fifteen_count ** 2)) + (0.5 * fifteen_count))
        answer = three_sum + five_sum - fifteen_sum
        return answer

    def euler2(self):
        previous_num = 1
        current_num = 2
        answer = 0
        while current_num < 4000000:
            if current_num % 2 == 0:
                answer += current_num
            new_num = current_num + previous_num
            previous_num = current_num
            current_num = new_num
        return answer

    def euler3(self):
        limit = 600851475143
        factor_limit = int(math.floor(math.sqrt(limit)))
        biggest_prime_factor = 1
        for i in range(1, factor_limit):
            if limit % i == 0:
                check_prime = i
                check_prime_limit = int(math.floor(math.sqrt(check_prime)))
                check_prime_factor = 1
                for j in range(1, check_prime_limit):
                    if check_prime % j == 0:
                        check_prime_factor = j
                if check_prime_factor == 1:
                    biggest_prime_factor = i
        return biggest_prime_factor

    def euler4(self):
        biggest_palandrome = 0
        biggest_palandrome_x = 0
        biggest_palandrome_y = 0
        stop_loop = 100
        for x in range(999, 100, -1):
            if x < stop_loop:
                break
            for y in range(999, x, -1):
                product = x * y
                reverse_product = int(str(product)[::-1])
                if product == reverse_product and product > biggest_palandrome:
                    biggest_palandrome = product
                    biggest_palandrome_x = x
                    biggest_palandrome_y = y
                    stop_loop = int(math.floor(biggest_palandrome / 999))
        return "answer is: {} = {}x{}".format(biggest_palandrome, biggest_palandrome_x, biggest_palandrome_y)

    def euler5(self):
        factors = {}
        maximum = 20
        for num in range(1, maximum + 1):
            for x in range(1, num + 1):
                if num % x == 0:
                    if self.check_prime(x):
                        if x not in factors:
                            factors[x] = 1
                        divides_count = 1
                        for attempt in range(1, 6):
                            if num % (x ** attempt) == 0:
                                divides_count = attempt
                        if factors[x] < divides_count:
                            factors[x] = divides_count
        answer = 1
        for prime, power in factors.items():
            answer = answer * (prime ** power)
        return answer

    def euler6(self):
        answer = 0
        for x in range(1, 101):
            answer = answer + x * (0.5 * (101 ** 2) - 0.5 * 101) - x ** 2
        return answer

    def euler7(self):
        num_primes = 0
        test = 1
        prime = 1
        while num_primes < 10001:
            test += 1
            if self.check_prime(test):
                num_primes += 1
                prime = test
        return prime

    def euler8(self):
        # Get SimplifyFraction function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("simplify fraction")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: SimplifyFraction
        # Calculate
        string_file = open("store/euler/euler_8_string.txt", "r")
        string = string_file.read()[:-1]
        string_file.close()
        biggest_product = 0
        while len(string) >= 13:
            substring = string[0:13]
            product = function_obj.list_product([int(x) for x in substring])
            biggest_product = max(product, biggest_product)
            string = string[1:]
        return biggest_product

    def euler9(self):
        answer_a = 0
        answer_b = 0
        answer_c = 0
        answer = 0
        for b in range(500, 0, -1):
            for a in range(b - 1, 0, -1):
                c = math.sqrt(a ** 2 + b ** 2)
                if c - math.floor(c) <= 0.001 and a + b + int(c) == 1000:
                    answer_a = a
                    answer_b = b
                    answer_c = int(c)
                    answer = a * b * int(c)
        return "a = {}, b = {}, c = {} and a*b*c = {}".format(answer_a, answer_b, answer_c, answer)

    def euler10(self):
        numbers = [0] * 2000000
        prime_sum = 2
        for x in range(3, 2000000, 2):
            if numbers[x] == 0:
                prime_sum = prime_sum + x
                for y in range(x, 2000000, x):
                    numbers[y] = 1
        return prime_sum

    def euler11(self):
        raw_box_file = open("store/euler/euler_11_grid.txt", "r")
        raw_box = raw_box_file.read()[:-1]
        raw_box_file.close()
        arr_box = raw_box.split()
        biggest_product = 0
        answer_x = 0
        answer_y = 0
        direction = ''
        # vertical checks
        for x in range(0, 20):
            for y in range(0, 17):
                product = int(arr_box[x + 20 * y]) * int(arr_box[x + 20 * y + 20]) * int(arr_box[x + 20 * y + 40]) * \
                          int(arr_box[x + 20 * y + 60])
                if product > biggest_product:
                    biggest_product = product
                    answer_x = x
                    answer_y = y
                    direction = "vertical"
        # horizontal checks
        for x in range(0, 17):
            for y in range(0, 20):
                product = int(arr_box[x + 20 * y]) * int(arr_box[x + 20 * y + 1]) * int(arr_box[x + 20 * y + 2]) * \
                          int(arr_box[x + 20 * y + 3])
                if product > biggest_product:
                    biggest_product = product
                    answer_x = x
                    answer_y = y
                    direction = "horizontal"
        # diagonal check \
        for x in range(0, 17):
            for y in range(0, 17):
                product = int(arr_box[x + 20 * y]) * int(arr_box[x + 20 * y + 21]) * int(arr_box[x + 20 * y + 42]) * \
                          int(arr_box[x + 20 * y + 63])
                if product > biggest_product:
                    biggest_product = product
                    answer_x = x
                    answer_y = y
                    direction = "diagonal \\"
        # diagonal check /
        for x in range(3, 20):
            for y in range(0, 17):
                product = int(arr_box[x + 20 * y]) * int(arr_box[x + 20 * y + 19]) * int(arr_box[x + 20 * y + 38]) * \
                          int(arr_box[x + 20 * y + 57])
                if product > biggest_product:
                    biggest_product = product
                    answer_x = x
                    answer_y = y
                    direction = "diagonal /"
        output_string = "biggest product is: {} the coords are: ({},{}) in the direction: {}".format(biggest_product,
                                                                                                     answer_x,
                                                                                                     answer_y,
                                                                                                     direction)
        return output_string

    def euler12(self):
        number = 1
        num_factors = 0
        while num_factors < 500:
            number += 1
            if number % 2 == 0:
                num_factors = self.find_number_of_factors(number + 1) * self.find_number_of_factors(number / 2)
            else:
                num_factors = self.find_number_of_factors((number + 1) / 2) * self.find_number_of_factors(number)
        triangle = ((number + 1) * number) / 2
        return triangle

    def euler13(self):
        arr_numbers_file = open("store/euler/euler_13_numbers.txt", "r")
        arr_numbers = arr_numbers_file.read()[:-1].split("\n")
        arr_numbers_file.close()
        total = 0
        for number in arr_numbers:
            total += int(number)
        return str(total)[0:10]

    def euler14(self):
        lengths = [0] * 1000000
        max_chain = 0
        max_start = 0
        for start in range(1, 1000000):
            num = start
            length = 1
            while True:
                if num == 1:
                    lengths[start] = length
                    break
                if num < 1000000 and lengths[num] != 0:
                    lengths[start] = length + lengths[num]
                    break
                if num % 2 == 0:
                    num //= 2
                    length += 1
                else:
                    num = (3 * num) + 1
                    length += 1
            if max_chain < lengths[start]:
                max_chain = lengths[start]
                max_start = start
        return max_start

    def euler15(self):
        grid_size = 20
        x = grid_size
        routes = 1
        for y in range(x):
            routes = routes * (x + y + 1) / (y + 1)
        return routes

    def euler16(self):
        big_number = 2 ** 1000
        big_number = str(big_number)
        total = 0
        for x in range(len(big_number)):
            total += int(big_number[x])
        return total

    def euler17(self):
        # Get Number function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("number")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: NumberWord
        # Do processing
        total = 0
        for x in range(1, 1001):
            total += len(function_obj.number_word(str(x)).replace(' ', '').replace('-', ''))
        return total

    def euler18(self):
        arr_triangle_file = open("store/euler/euler_18_triangle.txt", "r")
        arr_triangle = arr_triangle_file.read()[:-1].split("\n")
        arr_triangle_file.close()
        arr_triangle_val = {}
        for x in range(len(arr_triangle)):
            arr_triangle_val[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle_val) - 2, -1, -1):
            for col in range(len(arr_triangle_val[row])):
                if int(arr_triangle_val[row + 1][col]) > int(arr_triangle_val[row + 1][col + 1]):
                    arr_triangle_val[row][col] = int(arr_triangle_val[row][col]) + \
                                                 int(arr_triangle_val[row + 1][col])
                else:
                    arr_triangle_val[row][col] = int(arr_triangle_val[row][col]) + \
                                                 int(arr_triangle_val[row + 1][col + 1])
        return arr_triangle_val[0][0]

    def euler19(self):
        day = 1 + 365
        year = 0
        total = 0
        while year < 101:
            year += 1
            for month in range(12):
                if day % 7 == 0:
                    total += 1
                if month == 2:
                    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                        day += 29
                    else:
                        day += 28
                elif month in [9, 11, 4, 6]:
                    day += 30
                else:
                    day += 31
        return total

    def euler20(self):
        number = math.factorial(100)
        number = str(number)
        total = 0
        for x in range(len(number)):
            total += int(number[x])
        return total

    def euler21(self):
        amicable = []
        total = 0
        for x in range(10000):
            if x not in amicable:
                factors = self.find_factors(x)
                factor_total = 0
                for factor in factors:
                    factor_total = factor_total + factor
                other_number = factor_total - x
                other_factors = self.find_factors(other_number)
                other_factor_total = 0
                for other_factor in other_factors:
                    other_factor_total = other_factor_total + other_factor
                if other_factor_total - other_number == x and other_number != x:
                    self.mHalloObject.printer.output_raw("found a pair: {} and {}".format(x, factor_total-x))
                    amicable.append(x)
                    amicable.append(factor_total - x)
                    total = total + x + other_number
        return total

    def euler22(self):
        raw_names_file = open("store/euler/euler_22_names.txt", "r")
        raw_names = raw_names_file.read()[:-1]
        raw_names_file.close()
        arr_names = sorted(raw_names.replace('"', '').split(','))
        total = 0
        name_name = 0
        for name in arr_names:
            name_name += 1
            value = 0
            for letter in range(len(name)):
                value = value + ord(name[letter]) - 64
            score = value * name_name
            total += score
        return total

    def euler23(self):
        abundant_numbers = []
        sum_of_two = [0] * 28150
        total = (28150 / 2) * (1 + 28150) - 28150
        for x in range(28150):
            factors = self.find_factors(x)
            factor_total = 0
            for factor in factors:
                factor_total = factor_total + factor
            factor_total = factor_total - x
            if factor_total > x:
                abundant_numbers.append(x)
                for other_number in abundant_numbers:
                    ab_sum = other_number + x  # type: int
                    if ab_sum < 28150:
                        if sum_of_two[ab_sum] != 1:
                            sum_of_two[ab_sum] = 1
                            total -= ab_sum
                    else:
                        break
        return total

    def euler24(self):
        digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        permutation = 1000000 - 1
        string = ''
        while len(digits) != 1:
            number = int(math.floor(permutation / math.factorial(len(digits) - 1)))
            string += str(digits[number])
            del digits[number]
            permutation -= int(math.factorial(len(digits)) * number)
        string += str(digits[0])
        return string

    def euler25(self):
        length = 0
        a = 1
        b = 1
        num = 2
        while length < 1000:
            num += 1
            c = a + b
            a = b
            b = c
            length = len(str(c))
        return num

    def euler26(self):
        # Get PrimeFactors function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("prime factors")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: PrimeFactors
        # Do processing
        max_nines = 0
        max_d = 0
        for d in range(1, 1000):
            factors = function_obj.find_prime_factors(d)
            factors = self.remove_list_items(factors, 2)
            factors = self.remove_list_items(factors, 5)
            product = 1
            for factor in factors:
                product = product * factor
            #            print "d = " + str(d) + ", product = " + str(product)
            nines = 0
            while True:
                nines = (nines * 10) + 9
                if nines % product == 0:
                    if nines > max_nines:
                        max_nines = nines
                        max_d = d
                    # print "New record: " + str(d) + " requires " + str(len(str(nines))) + " nines."
                    break
        return max_d

    def euler27(self):
        max_length = 0
        max_product = 1
        for b in range(1, 1000):
            if self.check_prime(b):
                for a in range(1, 1000):
                    length = 0
                    n = 0
                    while True:
                        length += 1
                        n += 1
                        answer = (n ** 2) + (a * n) + b
                        if not self.check_prime(answer):
                            break
                    if length > max_length:
                        max_length = length
                        max_product = a * b
                    # print "new record: a = " + str(a) + ", b = " + str(b) + ", length = " + str(length)
                    length = 0
                    n = 0
                    if a < b:
                        while True:
                            length += 1
                            n += 1
                            answer = (n ** 2) - (a * n) + b
                            if not self.check_prime(answer):
                                break
                        if length > max_length:
                            max_length = length
                            max_product = -(a * b)
                        # print "new record: a = -" + str(a) + ", b = " + str(b) + ", length = " + str(length)
        return max_product

    def euler28(self):
        total = 1
        n = 1
        for x in range(1, 501):
            gap = x * 2
            total = total + 4 * n + 10 * gap
            n += gap * 4
        return total

    def euler29(self):
        # Get PrimeFactors function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("prime factors")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: PrimeFactors
        # Do processing
        answers = []
        for a in range(2, 101):
            a_factors = function_obj.find_prime_factors(a)
            #            answer = a
            for b in range(2, 101):
                #                answer = answer * a
                answer = sorted(b * a_factors)
                if answer not in answers:
                    answers.append(answer)
        return len(answers)

    def euler30(self):
        #        number = 10
        #        while True:
        power_digits = []
        for digit in range(10):
            power_digits.append(digit ** 5)
        total = 0
        for number in range(10, 200000):
            str_number = str(number)
            len_number = len(str_number)
            number_total = 0
            for x in range(len_number):
                number_total = number_total + power_digits[int(str_number[x])]
            if number_total == number:
                total = total + number
        return total

    def euler31(self):
        # Get ChangeOptions function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("change options")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: ChangeOptions
        # Do processing
        coins = [200, 100, 50, 20, 10, 5, 2, 1]
        options = function_obj.change_options(coins, 0, 200)
        num_options = len(options)
        #        num_options = euler.fnn_euler_changecount(self,coins,0,200)
        return num_options

    def euler32(self):
        digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        products = []
        for a in range(9):
            a_digit = digits[a]
            a_digits = list(digits)
            a_digits.remove(a_digit)
            for b in range(8):
                b_digit = a_digits[b]
                b_digits = list(a_digits)
                b_digits.remove(b_digit)
                for c in range(7):
                    c_digit = b_digits[c]
                    c_digits = list(b_digits)
                    c_digits.remove(c_digit)
                    for d in range(6):
                        d_digit = c_digits[d]
                        d_digits = list(c_digits)
                        d_digits.remove(d_digit)
                        for e in range(5):
                            e_digit = d_digits[e]
                            e_digits = list(d_digits)
                            e_digits.remove(e_digit)
                            product_one = (a_digit * 10 + b_digit) * (c_digit * 100 + d_digit * 10 + e_digit)
                            product_two = a_digit * (b_digit * 1000 + c_digit * 100 + d_digit * 10 + e_digit)
                            fail_one = False
                            fail_two = False
                            for f in range(4):
                                if str(e_digits[f]) not in list(str(product_one)) or product_one > 9999:
                                    fail_one = True
                            for g in range(4):
                                if (str(e_digits[g]) not in list(
                                        str(product_two)) or product_two < 1000 or product_two > 9999):
                                    fail_two = True
                            if not fail_one:
                                self.mHalloObject.printer.output_raw(str(a_digit) + str(b_digit) + "*" + str(c_digit) +
                                                                     str(d_digit) + str(e_digit) + "=" +
                                                                     str(product_one))
                                products.append(product_one)
                            if not fail_two:
                                self.mHalloObject.printer.output_raw(str(a_digit) + "*" + str(b_digit) + str(c_digit) +
                                                                     str(d_digit) + str(e_digit) + "=" +
                                                                     str(product_two))
                                products.append(product_two)
        products = list(set(products))
        return sum(products)

    def euler33(self):
        # Get PrimeFactors function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("prime factors")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: PrimeFactors
        simp_frac_class = function_dispatcher.get_function_by_name("simplify fraction")
        simp_frac_obj = function_dispatcher.get_function_object(simp_frac_class)  # type: SimplifyFraction
        # Do processing
        epsilon = 0.0000001
        total_numerator_factors = []
        total_denominator_factors = []
        for denominator in range(11, 100):
            for numerator in range(10, denominator):
                if str(numerator)[0] in str(denominator):
                    if str(denominator)[0] == str(denominator)[1]:
                        denominator_new = int(str(denominator)[1])
                    else:
                        denominator_new = int(str(denominator).replace(str(numerator)[0], ''))
                    numerator_new = int(str(numerator)[1])
                    numerator_factors_new = function_obj.find_prime_factors(numerator_new)
                    denominator_factors_new = function_obj.find_prime_factors(denominator_new)
                    if denominator_new != 0:
                        if (numerator / denominator - numerator_new / denominator_new) ** 2 < epsilon:
                            self.mHalloObject.printer.output_raw("found one. {}/{}".format(numerator, denominator))
                            total_numerator_factors += numerator_factors_new
                            total_denominator_factors += denominator_factors_new
                elif str(numerator)[1] in str(denominator) and str(numerator)[1] != "0":
                    if str(denominator)[0] == str(denominator)[1]:
                        denominator_new = int(str(denominator)[1])
                    else:
                        denominator_new = int(str(denominator).replace(str(numerator)[1], ''))
                    numerator_new = int(str(numerator)[0])
                    numerator_factors_new = function_obj.find_prime_factors(numerator_new)
                    denominator_factors_new = function_obj.find_prime_factors(denominator_new)
                    if denominator_new != 0:
                        if (numerator / denominator - numerator_new / denominator_new) ** 2 < epsilon:
                            self.mHalloObject.printer.output_raw("found one. {}/{}".format(numerator, denominator))
                            total_numerator_factors = total_numerator_factors + numerator_factors_new
                            total_denominator_factors = total_denominator_factors + denominator_factors_new
        total_denominator_factors_new = simp_frac_obj.list_minus(total_denominator_factors,
                                                                 simp_frac_obj.list_intersection(
                                                                     total_denominator_factors,
                                                                     total_numerator_factors))
        total_denominator_new = simp_frac_obj.list_product(total_denominator_factors_new)
        return total_denominator_new

    def euler34(self):
        total_sum = 0
        factorials = [math.factorial(x) for x in range(10)]
        for x in range(3, 10 ** 6):
            strx = str(x)
            total = 0
            for number in strx:
                total += factorials[int(number)]
            if total == x:
                total_sum += x
        return total_sum

    def euler35(self):
        number = 0
        for x in range(10 ** 6):
            prime = True
            strx = str(x)
            for digit in range(len(strx)):
                rotatex = strx[digit:] + strx[:digit]
                prime = prime and self.check_prime(int(rotatex))
            if prime:
                number += 1
                self.mHalloObject.printer.output_raw(x)
        return number

    def euler36(self):
        total = 0
        for a in range(10 ** 6):
            if self.check_palindrome(str(a)):
                binary = bin(a)[2:]
                if self.check_palindrome(binary):
                    total += a
        return total

    def euler37(self):
        total = 0
        num_found = 0
        number = 10
        while num_found < 11 and number < 10 ** 7:
            str_number = str(number)
            truncatable = True
            for x in range(len(str_number)):
                truncatable = truncatable and self.check_prime(int(str_number[x:]))
                truncatable = truncatable and self.check_prime(int(str_number[:len(str_number) - x]))
            if truncatable:
                self.mHalloObject.printer.output_raw("found one. {}".format(str_number))
                num_found += 1
                total += number
            number += 1
        return total

    def euler38(self):
        max_constr = 0
        for x in range(10 ** 5):
            constr = ''
            n = 1
            while len(constr) < 9:
                constr += str(x * n)
                n += 1
            if len(constr) == 9 and int(constr) > max_constr:
                if self.check_list_in_list([str(x) for x in list(range(1, 10))], list(constr)):
                    self.mHalloObject.printer.output_raw("new max: {}".format(constr))
                    max_constr = int(constr)
        return max_constr

    def euler39(self):
        epsilon = 0.00000001
        max_p = 0
        max_p_count = 0
        for p in range(1, 1001):
            p_count = 0
            p_list = []
            for a in range(1, int(p / 2)):
                b = (p * p - 2 * p * a) / (2 * (a - p))
                c = (a * a + b * b) ** 0.5
                if b % 1 < epsilon and c % 1 < epsilon:
                    p_count += 1
                    p_list.append([int(a), int(b), int(c)])
            if p_count > max_p_count:
                max_p = p
                max_p_count = p_count
        return "Maximum triangles for given perimeter is {} for the perimeter of {}.".format(max_p_count, max_p)

    def euler40(self):
        string_length = 0
        product = 1
        for number in range(1, 10 ** 6):
            add_length = len(str(number))
            if string_length < 1 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[1 - string_length - 1]))
                product *= int(str(number)[1 - string_length - 1])
            if string_length < 10 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[10 - string_length - 1]))
                product *= int(str(number)[10 - string_length - 1])
            if string_length < 100 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[100 - string_length - 1]))
                product *= int(str(number)[100 - string_length - 1])
            if string_length < 1000 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[1000 - string_length - 1]))
                product *= int(str(number)[1000 - string_length - 1])
            if string_length < 10000 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[10000 - string_length - 1]))
                product *= int(str(number)[10000 - string_length - 1])
            if string_length < 100000 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[100000 - string_length - 1]))
                product *= int(str(number)[100000 - string_length - 1])
            if string_length < 1000000 <= string_length + add_length:
                self.mHalloObject.printer.output_raw("digit is {}".format(str(number)[1000000 - string_length - 1]))
                product *= int(str(number)[1000000 - string_length - 1])
            string_length += add_length
        return product

    def euler41(self):
        max_pandigital_prime = 1
        for x in range(2, 8 * 10 ** 6):
            digits = len(str(x))
            if x % 2 != 0 and x % 3 != 0 and x % 5 != 0:
                if self.check_list_in_list([str(x) for x in range(1, digits + 1)], list(str(x))):
                    if self.check_prime(x):
                        self.mHalloObject.printer.output_raw("this is one. {}".format(x))
                        max_pandigital_prime = x
        return max_pandigital_prime

    def euler42(self):
        file_string_file = open("store/euler/euler_42_words.txt", "r")
        file_string = file_string_file.read()[:-1]
        file_string_file.close()
        words = [word.replace('"', '') for word in file_string.split(',')]
        longest_word = max(words, key=len)
        triangles = []
        count = 0
        x = 1
        while (0.5 * x * (x + 1)) < 26 * len(longest_word):
            triangles.append(0.5 * x * (x + 1))
            x += 1
        for word in words:
            if self.find_word_value(word) in triangles:
                self.mHalloObject.printer.output_raw("found a triangle word: {}".format(word))
                count += 1
        return count

    def euler43(self):
        pandigitals = self.get_list_pandigitals()
        pandigital_sum = 0
        for pandigital in pandigitals:
            if (int(str(pandigital)[1:4]) % 2 == 0 and int(str(pandigital)[2:5]) % 3 == 0 and int(
                    str(pandigital)[3:6]) % 5 == 0 and int(str(pandigital)[4:7]) % 7 == 0 and int(
                    str(pandigital)[5:8]) % 11 == 0):
                if int(str(pandigital)[6:9]) % 13 == 0 and int(str(pandigital)[7:10]) % 17 == 0:
                    self.mHalloObject.printer.output_raw("found one: ".format(pandigital))
                    pandigital_sum += pandigital
        return pandigital_sum

    def euler44(self):
        epsilon = 0.000001
        pentagonals = [0, 1]
        smallest_diff = 10 ** 9
        for x in range(2, 3000):
            pentagonals.append(int(x * (3 * x - 1) / 2))
            for y in range(1, x):
                pentagonal_sum = pentagonals[x] + pentagonals[y]
                diff = pentagonals[x] - pentagonals[y]
                sum_pent = (1 + (1 + 24 * pentagonal_sum) ** 0.5) / 6
                diff_pent = (1 + (1 + 24 * diff) ** 0.5) / 6
                if sum_pent % 1 < epsilon and diff_pent % 1 < epsilon:
                    self.mHalloObject.printer.output_raw('found one.')
                    if diff < smallest_diff:
                        smallest_diff = diff
        return smallest_diff

    def euler45(self):
        epsilon = 0.00001
        tri_pent_hex = 0
        for x_hex in range(144, 10 ** 5):
            x = x_hex * (2 * x_hex - 1)
            x_tri = (-1 + (1 + 8 * x) ** 0.5) / 2
            if abs(x_tri - round(x_tri)) % 1 < epsilon:
                x_pent = (1 + (1 + 24 * x) ** 0.5) / 6
                if abs(x_pent - round(x_pent)) % 1 < epsilon:
                    self.mHalloObject.printer.output_raw('found it.')
                    tri_pent_hex = x
                    break
        return tri_pent_hex

    def euler46(self):
        num = 1
        while True:
            num += 2
            if self.check_prime(num):
                continue
            double_square_num = 0
            double_square = 2 * double_square_num * double_square_num
            found = True
            while double_square < num:
                double_square_num += 1
                double_square = 2 * double_square_num * double_square_num
                if self.check_prime(num - double_square):
                    found = False
            if found:
                return num

    def euler47(self):
        # Get PrimeFactors function
        function_dispatcher = self.mHalloObject.function_dispatcher
        function_class = function_dispatcher.get_function_by_name("prime factors")
        function_obj = function_dispatcher.get_function_object(function_class)  # type: PrimeFactors
        # Solve
        num = 1
        streak = 4
        running_count = 0
        answer = 0
        while True:
            num += 1
            len_prime_factors = len(set(function_obj.find_prime_factors(num)))
            if len_prime_factors != streak:
                running_count = 0
                continue
            running_count += 1
            if running_count == streak:
                answer = num + 1 - streak
                break
        return answer

    def euler48(self):
        num = 0
        for x in range(1, 1001):
            num += x ** x
            num %= 10 ** 12
        return num % 10 ** 10

    def euler49(self):
        answer = None
        for x in range(10 ** 3, 10 ** 4 + 1):
            if x == 1487:
                continue
            if not self.check_prime(x):
                continue
            perms_x = [int(''.join(p)) for p in itertools.permutations(str(x))]
            for perm_x in perms_x:
                if perm_x == x:
                    continue
                if len(str(perm_x)) != 4:
                    continue
                if not self.check_prime(perm_x):
                    continue
                diff = perm_x - x
                next_perm_x = x + 2 * diff
                if next_perm_x not in perms_x:
                    continue
                if len(str(next_perm_x)) != 4:
                    continue
                if self.check_prime(next_perm_x):
                    self.mHalloObject.printer.output_raw("found it")
                    self.mHalloObject.printer.output_raw(x)
                    self.mHalloObject.printer.output_raw(x + diff)
                    self.mHalloObject.printer.output_raw(x + 2 * diff)
                    answer = str(x) + str(x + diff) + str(x + 2 * diff)
                    break
            if answer is not None:
                break
        return answer

    def euler50(self):
        longest_chain = 0
        longest_total = 0
        chain = []
        for x in range(1, 10 ** 4):
            if not self.check_prime(x):
                continue
            chain.append(x)
            for temp_chain in [chain[-x:] for x in range(longest_chain, len(chain))]:
                if sum(temp_chain) > 10 ** 6:
                    continue
                if not self.check_prime(sum(temp_chain)):
                    continue
                if len(temp_chain) > longest_chain:
                    longest_chain = len(temp_chain)
                    longest_total = sum(temp_chain)
        return longest_total

    def euler51(self):
        num = 0
        solved = False
        while True:
            num += 1
            if not self.check_prime(num):
                continue
            for digit in range(len(str(num))):
                failures = 0
                for x in range(10):
                    temp_num = int(str(num).replace(str(num)[digit], str(x)))
                    if len(str(temp_num)) != len(str(num)) or not self.check_prime(temp_num):
                        failures += 1
                if failures <= 2:
                    self.mHalloObject.printer.output_raw(num)
                    solved = True
                    break
            if solved:
                break
        return num

    def euler52(self):
        # Get SimplifyFraction function
        function_dispatcher = self.mHalloObject.function_dispatcher
        simp_frac_class = function_dispatcher.get_function_by_name("simplify fraction")
        simp_frac_obj = function_dispatcher.get_function_object(simp_frac_class)  # type: SimplifyFraction
        # Do processing
        num = 0
        while True:
            num += 1
            num_list = list(str(num))
            if num_list != simp_frac_obj.list_intersection(num_list, list(str(2 * num))):
                continue
            if num_list != simp_frac_obj.list_intersection(num_list, list(str(3 * num))):
                continue
            if num_list != simp_frac_obj.list_intersection(num_list, list(str(4 * num))):
                continue
            if num_list != simp_frac_obj.list_intersection(num_list, list(str(5 * num))):
                continue
            if num_list != simp_frac_obj.list_intersection(num_list, list(str(6 * num))):
                continue
            self.mHalloObject.printer.output_raw(num)
            break
        return num

    def euler53(self):
        num = 0
        for n in range(23, 101):
            for r in range(n):
                ncr_value = math.factorial(n) / (math.factorial(r) * math.factorial(n - r))
                if ncr_value > 10 ** 6:
                    num += 1
        return num

    def euler54(self):
        list_poker_games_file = open("store/euler/euler_54_poker.txt", "r")
        list_poker_games = list_poker_games_file.read().split("\n")
        list_poker_games_file.close()
        total_wins = 0
        for poker_game in list_poker_games:
            deck = Deck()
            hand_one = Hand.from_two_letter_code_list(deck, poker_game.split()[:5])
            hand_two = Hand.from_two_letter_code_list(deck, poker_game.split()[5:])
            if hand_one.poker_beats(hand_two):
                total_wins += 1
        return total_wins

    def euler55(self):
        total = 0
        for num in range(10 ** 4):
            temp_num = num
            is_lychell = True
            for _ in range(50):
                temp_num += int(str(temp_num)[::-1])
                if self.check_palindrome(str(temp_num)):
                    is_lychell = False
                    break
            if is_lychell:
                total += 1
        return total

    def euler56(self):
        max_digits = 0
        for a in range(100):
            for b in range(100):
                power = a ** b
                sum_digits = sum([int(x) for x in list(str(power))])
                max_digits = max(max_digits, sum_digits)
        return max_digits

    def euler57(self):
        numerator = 3
        denominator = 2
        total = 0
        # Do 1000 iterations
        for _ in range(10 ** 3):
            # If numerator is longer than denominator, add to total
            if len(str(numerator)) > len(str(denominator)):
                total += 1
            # Add 1 to fraction
            numerator += denominator
            # Flip fraction
            temp = numerator
            numerator = denominator
            denominator = temp
            # Add 1 to fraction
            numerator += denominator
        return total

    def euler58(self):
        num_diag_primes = 0
        gap = 0
        num = 1
        while True:
            gap += 2
            for gap_num in range(1, 4):
                if self.check_prime(num + (gap_num * gap)):
                    num_diag_primes += 1
            num += 4 * gap
            total = gap * 2 + 1
            if num_diag_primes * 10 < total:
                break
        length = gap + 1
        return length

    def euler59(self):
        # Get cipher data
        raw_file = open("store/euler/euler_59_cipher.txt", "r")
        raw = raw_file.read()
        raw_file.close()
        raw_list = [int(x) for x in raw.split(",")]
        # Get 3 blank lists, to unzip the list into
        list_one = []
        list_two = []
        list_thr = []
        # Loop through the list, putting first element in list 1, second in list 2, etc
        for a in range(len(raw_list)):
            if a % 3 == 1:
                list_one.append(raw_list[a])
            if a % 3 == 2:
                list_two.append(raw_list[a])
            if a % 3 == 0:
                list_thr.append(raw_list[a])
        # Find the most common character in each list
        common_one = max(set(list_one), key=list_one.count)
        common_two = max(set(list_two), key=list_two.count)
        common_thr = max(set(list_thr), key=list_thr.count)
        # Find the keys for each list, assuming most common char is space
        key_one = ord(" ") ^ common_one
        key_two = ord(" ") ^ common_two
        key_thr = ord(" ") ^ common_thr
        # Put the string back together, get sum of ascii values
        sum_values = 0
        for a in range(len(raw_list)):
            char_value = ""
            if a % 3 == 1:
                char_value = raw_list[a] ^ key_one
            if a % 3 == 2:
                char_value = raw_list[a] ^ key_two
            if a % 3 == 0:
                char_value = raw_list[a] ^ key_thr
            sum_values += char_value
        self.mHalloObject.printer.output_raw("Total: {}".format(sum_values))
        return sum_values

    def euler60(self):
        big_dict = {}
        num = 1
        while True:
            num += 2
            if not self.check_prime(num):
                continue
            big_dict[num] = {}
            for num_one in big_dict:
                if num_one == num:
                    continue
                check = self.check_concat_primes(num, num_one)
                if not check:
                    continue
                big_dict[num_one][num] = {}
                for num_two in big_dict[num_one]:
                    if num_two == num:
                        continue
                    check = self.check_concat_primes(num, num_two)
                    if not check:
                        continue
                    big_dict[num_one][num_two][num] = {}
                    for num_three in big_dict[num_one][num_two]:
                        if num_three == num:
                            continue
                        check = self.check_concat_primes(num, num_three)
                        if not check:
                            continue
                        self.mHalloObject.printer.output_raw("Found fourlist {}".format([num_one,
                                                                                         num_two,
                                                                                         num_three,
                                                                                         num]))
                        big_dict[num_one][num_two][num_three][num] = {}
                        for num_four in big_dict[num_one][num_two][num_three]:
                            if num_four == num:
                                continue
                            check = self.check_concat_primes(num, num_four)
                            if not check:
                                continue
                            return "sum({}) = {}".format([num_one, num_two, num_three, num_four, num],
                                                         sum([num_one, num_two, num_three, num_four, num]))

    def euler67(self):
        # this is the same as  problem 18, but bigger file.
        arr_triangle_file = open("store/euler/euler_67_triangle.txt", "r")
        arr_triangle = arr_triangle_file.read()[:-1].split("\n")
        arr_triangle_file.close()
        arr_triangle_val = {}
        for x in range(len(arr_triangle)):
            arr_triangle_val[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle_val) - 2, -1, -1):
            for col in range(len(arr_triangle_val[row])):
                if int(arr_triangle_val[row + 1][col]) > int(arr_triangle_val[row + 1][col + 1]):
                    arr_triangle_val[row][col] = int(arr_triangle_val[row][col]) + \
                                                 int(arr_triangle_val[row + 1][col])
                else:
                    arr_triangle_val[row][col] = int(arr_triangle_val[row][col]) + \
                                                 int(arr_triangle_val[row + 1][col + 1])
        return arr_triangle_val[0][0]

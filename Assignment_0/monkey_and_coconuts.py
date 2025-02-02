"""
IS597PR - J. Weible
CORRECT all syntax & formatting mistakes in this program so it works properly.

Brute-force (inefficient) solver of the "Monkey and the Coconuts" puzzle.

This is an example of a "Diophantine problem" -- one which implies a system of
algebraic equations where only integer solution(s) are valid.

I learned of it from the opening chapter of "The Colossal Book of Mathematics"
by Martin Gardner. Ben Williams' popularized the problem of these parameters
in a Saturday Evening Post Story:

    Five men and a monkey were shipwrecked on an island. They spent the first
    day gathering coconuts. During the night, one man woke up and decided to
    take his share of the coconuts. He divided them into five equal piles. One
    coconut was left over so he gave it to the monkey, then hid his share,
    put the rest back together, and went back to sleep.

    Soon a second man woke up and did the same thing. After dividing the
    coconuts into five equal piles, one coconut was left over which he gave to
    the monkey. He then hid his share, put the rest back together, and went to
    bed. The third, fourth and fifth man followed the exact same procedure.

    The next morning, after they all woke up, they divided the remaining
    coconuts into five equal shares. This time no coconuts were left over.

    How many coconuts were there in the original pile?

See https://en.wikipedia.org/wiki/The_monkey_and_the_coconuts for detailed
history, analysis and multiple ways this problem can be solved.
"""

# Fix 1 : Correct import syntax - "import" instead of "Import"
import sys

def solve_coconut_problem(number_of_men, monkey_gets_coconut_at_end,
                          maximum_number_to_try, verbose=False):
    """This algorithm starts at the beginning of the problem by trying numbers
    of coconuts before nightfall, and going through the divisions and thefts
    to see if it results in integers all the way to an equal potion in
    the morning. If so, a solution was found and will be printed and returned.

    :param number_of_men: how many men successively sneak "their share" during the night
    :param monkey_gets_coconut_at_end: False or True, whether 1 coconut gets left for the monkey
    :param maximum_number_to_try: the highest number of starting coconuts to test.
    :param verbose: whether to print while searching.
    :return: a list of solution(s) found [the starting number(s) of coconuts
    """

    solutions_found = []        # Fix : Semicolon is unnecessary

    # guess represents how many coconuts we might have started with
    for guess in range(0, maximum_number_to_try):
    # Fix 2 : Correct Indentation for the if statement below
        if verbose:
            # Using Python's f-string instead of .format() method
            print(f'Testing a start of {guess} coconut(s). ')


        coconuts = guess
        ok_so_far = True

        for man in range(1, number_of_men + 1):
            # Fix 3 : Correct Indentation for the if statement below
            if coconuts % number_of_men != 1:
                # Fix 4 : Correct Indentation for the content below

                # Quantity was not evenly divisible with a single remainder.
                # Fix 5 : Add if-statement colon(:) for verbose condition
                if verbose:
                    # Using Python's f-string instead of .format() method
                    print(f'Wrong because man #{man} would have found {coconuts} coconuts\n')
                ok_so_far = False
                break

            # Fix 6 : Correct the indentation of the code below - it exits the if condition above
            equal_share = coconuts // number_of_men   # Man takes his equal share
            coconuts -= equal_share         # Remaining coconuts after taking his share
            coconuts -= 1                   # Monkey gets one coconut

            if verbose:
                # Fix 7 : Correct the indentation of the code below
                print(f'man {man} took {equal_share}, gave monkey 1, and {coconuts} remain.')

        # Fix 8 : Correct the indentation of the code below
        if ok_so_far:
            # Check final conditions for the next morning
            # Fix 9 : Correct the check on final condition - remove \ escape character after the 'or'
            if(coconuts % number_of_men == 1 and monkey_gets_coconut_at_end) or (coconuts % number_of_men == 0 and not monkey_gets_coconut_at_end):
                # Fix 10 : Correct the indentation of the code below
                print(f'Solution found. They could have started with {guess:10,} coconuts.')
                solutions_found.append(guess)

    if not solutions_found:
        print(f"No solutions found with fewer than {maximum_number_to_try} starting coconuts.")

    return solutions_found

if __name__ == "__main__":
    print("Running Python:", sys.version_info, "\n")
    print("Searching for solutions using William's variation:")
    solve_coconut_problem(number_of_men=5, monkey_gets_coconut_at_end=False,
                          maximum_number_to_try=20000)

    # Fix 10 : Using Colon(:) with (try and except) statement instead of curly-brackets({ })
    try:
        print("\nNow try a custom variation:")
        sailors = int(input("How many sailors are on your island? "))

        # Adding .strip().upper() directly in the leftover variable declaration instead of in if statement
        leftover = input("Is there one coconut left for the monkey at the end? (Y/N) ").strip().upper()

        if leftover in ['T', 'Y', 'TRUE', 'YES']:
            leftover = True
        else:
            leftover = False

        solve_coconut_problem(number_of_men=sailors,
                              monkey_gets_coconut_at_end=leftover,
                              maximum_number_to_try=10000)
    except ValueError:
        print("Invalid input, try again.\n")
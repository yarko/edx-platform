""" Fuzz test for CustomResponse """

from capa.safe_exec import safe_exec
from codejail.safe_exec import SafeExecException
import random

from datetime import datetime
import sys
import traceback
import string
import os
import struct

# Use memcache running locally
CACHE_SETTINGS = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    },
}

# Configure settings so Django will let us import its cache wrapper
# Caching is the only part of Django being tested
from django.conf import settings 
settings.configure(CACHES=CACHE_SETTINGS)

from django.core.cache import cache

# Script to install as the checker for the CustomResponse
TEST_SCRIPT = u"""
# Import a library
import numpy

def check_func(expect, answer_given):
    # Looping and printin
    for i in range(0, 1234):
        print "Test"
        x = 5

    # While loop
    i = 0
    while i < 10:
        i += 1

    # Return a dict
    return {'ok': answer_given == expect, 'msg': 'Message text'}
"""

PRINTABLE_CHARS = [c for c in string.printable]
UNICODE_CHARS = [unichr(u) for u in range(0, 2**16)]
ALL_CHARS = PRINTABLE_CHARS + UNICODE_CHARS
def random_string(length=random.randint(0, 10)):
    """ Return a random string of the given length """
    chars = [random.choice(ALL_CHARS) for i in range(length)]
    return "".join(chars)

MAX_NUM_MUTATIONS = 5
def mutate_string(orig_string):
    """ Mutate `string` randomly, then return the mutated string """

    # Copy the string
    mutated_string = orig_string

    # Mutate a random number of characters
    for i in range(0, random.randint(1, MAX_NUM_MUTATIONS)):
        
        # Choose a random index in the string
        index = random.randint(1, len(mutated_string) - 1)

        # Choose a random character to change it to
        new_char = random.choice(ALL_CHARS)

        # Replace the character 
        mutated_string = mutated_string[0:index-1] + new_char + mutated_string[index+1:]

    return mutated_string

def generate_random_inputs(seed):
    """ Deterministically generate input values for the fuzz test 
    from the random `seed`.
    
    Returns a dict with keys:
        
    * `problem_code` (string)
    * `random_seed` (int)
    * `globals_dict` (dictionary of globals)
    """

    # Seed the PRNG to get repeatable outputs
    random.seed(seed)

    # Create a dict to store the inputs
    inputs = {}

    # Create problem code by mutating existing problem
    inputs['problem_code'] = mutate_string(TEST_SCRIPT)

    # Random seed for the execution
    inputs['random_seed'] = random.randint(-10000, 10000)

    # Random globals dict
    inputs['globals_dict'] = {}
    for i in range(random.randint(1, 100)):
        inputs['globals_dict'][random_string()] = random_string()

    return inputs

NO_ERROR, SAFE_EXEC_ERROR, UNEXPECTED_ERROR = range(3)
def execute_test(problem_code="", random_seed=1, globals_dict=None):
    """ Execute the test using input arguments.
    Returns `(result, description)` tuple, where
    `result` is either NO_ERROR, SAFE_EXEC_ERROR, or UNEXPECTED_ERROR
    and `description` is a string describing the error """

    try:
        safe_exec(problem_code, globals_dict, random_seed=random_seed, cache=cache)

    # Ignore safe exec exceptions
    except SafeExecException:
        return (SAFE_EXEC_ERROR, None)

    # Exit if we're interrupted
    except KeyboardInterrupt:
        raise

    # Look out for unexpected errors
    except:
        return (UNEXPECTED_ERROR, traceback.format_exc())

    # Otherwise, no error
    else:
        return (NO_ERROR, None)

def run_fuzz_tests():
    """ Randomize student submission, check function, and hint function
    to see if we can break CustomResponse """

    # Maintain counts so we can figure out how far our inputs make it
    iteration_count = 0
    safe_exec_error_count = 0
    unexpected_error_count = 0
    no_error_count = 0

    # Create a (hopefully unique) file to write outputs to
    output_filename = 'results_{0}.txt'.format(str(datetime.now()))
    output_file = open(output_filename, "w")

    while True:
        try:
            # Choose a random seed for this test run
            seed = struct.unpack('i', os.urandom(4))[0]

            # Generate random inputs
            inputs = generate_random_inputs(seed)

            # Execute the test and see if we get an unexpected exception
            (result, description) = execute_test(**inputs)

            # Record the error, if we got one
            if result == UNEXPECTED_ERROR:
                output_file.write("\nERROR {0}: {1}\n".format(seed, description))
                unexpected_error_count += 1

            elif result == SAFE_EXEC_ERROR:
                safe_exec_error_count += 1

            else:
                no_error_count += 1

            # Print a status update every 100 iterations
            iteration_count += 1
            if iteration_count % 100 == 0:
                output_file.write(".")
                output_file.flush()

        except KeyboardInterrupt:
            msg = "Stopping tests at iteration {0} ({1} safe exec errors, {2} unexpected errors, {3} successes) ..."
            print msg.format(iteration_count, safe_exec_error_count, unexpected_error_count, no_error_count)
            output_file.close()
            exit(0)

def main():
    """ If we have arguments, interpret them as random seeds and print out the inputs.
    Otherwise, run fuzz tests until the user interrupts """

    if len(sys.argv) > 1:
        for seed in [int(arg) for arg in sys.argv[1:]]:
            inputs = generate_random_inputs(seed)
            print "{0}: {1}".format(seed, str(inputs))
    else:
        run_fuzz_tests()

if __name__ == '__main__':
    main()

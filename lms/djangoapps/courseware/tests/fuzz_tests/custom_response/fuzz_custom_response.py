""" Fuzz test for CustomResponse """

import capa.capa_problem as lcp
from capa.responsetypes import StudentInputError, ResponseError, LoncapaProblemError
from xmodule.x_module import ModuleSystem
import mock
import fs.osfs
import random

from datetime import datetime
import sys
import traceback
import string
import os
import lxml

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

PRINTABLE_CHARS = [c for c in string.printable]
#UNICODE_CHARS = [unichr(u) for u in range(0, 2**16)]
ALL_CHARS = PRINTABLE_CHARS #+ UNICODE_CHARS
def random_string(length=random.randint(0, 10)):
    """ Return a random string of the given length """
    chars = [random.choice(ALL_CHARS) for i in range(length)]
    return "".join(chars)

MAX_NUM_MUTATIONS = 5
def mutate_xml(xml):
    """ Mutate the `xml` string randomly, then return the mutated string """

    # Copy the string
    mutated_xml = xml

    # Mutate a random number of characters
    for i in range(0, random.randint(1, MAX_NUM_MUTATIONS)):
        
        # Choose a random index in the string
        index = random.randint(1, len(xml) - 1)

        # Choose a random character to change it to
        new_char = random.choice(ALL_CHARS)

        # Replace the character 
        mutated_xml = mutated_xml[0:index-1] + new_char + mutated_xml[index+1:]

    return mutated_xml

def generate_random_inputs(seed, problems):
    """ Deterministically generate input values for the fuzz test 
    from the random `seed`.
    
    Returns a dict with keys:
        
    * `problem_xml` (string)
    * `problem_seed` (int)
    * `student_submission` (string)
    """

    # Seed the PRNG to get repeatable outputs
    random.seed(seed)

    # Create a dict to store the inputs
    inputs = {}

    # Create problem XML by mutating an existing problem
    inputs['problem_xml'] = mutate_xml(random.choice(problems))

    # Random problem seed
    inputs['problem_seed'] = random.randint(0, 100000)

    # Random student submission string
    inputs['student_submission'] = random_string()

    return inputs

def system_mock():
    """ Create a mock ModuleSystem, installing our cache"""
    system = mock.MagicMock(ModuleSystem)
    system.render_template = lambda template, context: "<div>%s</div>" % template
    system.cache = cache
    system.filestore = mock.MagicMock(fs.osfs.OSFS)
    system.filestore.root_path = ""
    system.DEBUG = True

    return system

NO_ERROR, INVALID_XML, PROBLEM_SPECIFIC_ERROR, UNEXPECTED_ERROR = range(4)
def execute_test(problem_xml="", problem_seed=1, student_submission=""):
    """ Execute the test using input arguments.
    Returns `(result, description)` tuple, where
    `result` is either INVALID_XML, PROBLEM_SPECIFIC_ERROR, UNEXPECTED_ERROR, or NO_ERROR
    and `description` is a string describing the error """

    # Create the problem
    try:
        problem = lcp.LoncapaProblem(problem_xml, '1', state=None,
                                     seed=problem_seed, system=system_mock())

    # If we've generated invalid XML, then don't bother testing it
    except lxml.etree.XMLSyntaxError:
        return (INVALID_XML, None)

    # If we get a problem-specific error, report it
    except (StudentInputError, ResponseError, LoncapaProblemError):
        return (PROBLEM_SPECIFIC_ERROR, None)

    except KeyboardInterrupt:
        raise

    # Otherwise, we've broken the problem
    except:
        return (UNEXPECTED_ERROR, traceback.format_exc())

    # Submit an answer and try to grade the problem
    keys = ['1_{0}_1'.format(i) for i in range(2, 15)]
    values = [student_submission for i in range(2, 15)]
    answers = dict(zip(keys, values))

    try:
        problem.grade_answers(answers)

    # Ignore expected, capa-specific errors
    except (StudentInputError, ResponseError, LoncapaProblemError):
        return (PROBLEM_SPECIFIC_ERROR, None)

    except KeyboardInterrupt:
        raise

    except:
        # Report all other exceptions
        return (UNEXPECTED_ERROR, traceback.format_exc())

    else:
        return (NO_ERROR, None)

def run_fuzz_tests(problems):
    """ Randomize student submission, check function, and hint function
    to see if we can break CustomResponse """

    # Maintain counts so we can figure out how far our inputs make it
    iteration_count = 0
    invalid_xml_count = 0
    problem_error_count = 0

    # Create a (hopefully unique) file to write outputs to
    output_filename = 'results_{0}.txt'.format(str(datetime.now()))
    output_file = open(output_filename, "w")

    while True:
        try:
            # Choose a random seed for this test run
            seed = random.randint(0, 2**16)

            # Generate random inputs
            inputs = generate_random_inputs(seed, problems)

            # Execute the test and see if we get an unexpected exception
            (result, description) = execute_test(**inputs)

            # Record the error, if we got one
            if result == UNEXPECTED_ERROR:
                output_file.write("\nERROR {0}: {1}\n".format(seed, description))

            elif result == INVALID_XML:
                invalid_xml_count += 1

            elif result == PROBLEM_SPECIFIC_ERROR:
                problem_error_count += 1

            # Print a status update every 100 iterations
            iteration_count += 1
            if iteration_count % 100 == 0:
                output_file.write(".")
                output_file.flush()

        except KeyboardInterrupt:
            msg = "Stopping tests at iteration {0} ({1} xml errors, {2} problem-specific errors) ..."
            print msg.format(iteration_count, invalid_xml_count, problem_error_count)
            output_file.close()
            exit(0)

PROBLEMS_DIR = "problems"
def load_existing_problems():

    problems = []

    for path in sorted(os.listdir(PROBLEMS_DIR)):
        with open(os.path.join(PROBLEMS_DIR, path)) as problem_file:
            try:
                problem_str = problem_file.read()
            except:
                pass
            else:
                problems.append(problem_str)

    return problems

def main():
    """ If we have arguments, interpret them as random seeds and print out the inputs.
    Otherwise, run fuzz tests until the user interrupts """

    # Pre-load existing problems, which we will mutate later
    problems = load_existing_problems()

    if len(sys.argv) > 1:
        for seed in [int(arg) for arg in sys.argv[1:]]:
            inputs = generate_random_inputs(seed, problems)
            print "{0}: {1}".format(seed, str(inputs))
    else:
        run_fuzz_tests(problems)

if __name__ == '__main__':
    main()

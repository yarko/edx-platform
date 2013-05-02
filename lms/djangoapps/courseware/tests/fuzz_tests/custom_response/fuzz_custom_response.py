""" Fuzz test for CustomResponse """

from capa.tests.response_xml_factory import CustomResponseXMLFactory
import capa.capa_problem as lcp
from capa.responsetypes import StudentInputError, ResponseError, LoncapaProblemError
from xmodule.x_module import ModuleSystem
import mock
import fs.osfs
import random
import textwrap

import sys
import traceback

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

TEST_SCRIPT_TEMPLATE = u"""
        def check_func(expect, answer_given):
            # {0}
"""

UNICODE_CHARS = [unichr(char_code) for char_code in range(0, 2**16)]
def random_string(length=random.randint(0, 100000)):
    """ Return a random string of the given length """
    chars = [random.choice(UNICODE_CHARS) for i in range(length)]
    return "".join(chars)

def generate_random_inputs(seed):
    """ Deterministically generate input values for the fuzz test 
    from the random `seed`.
    
    Returns a dict with keys:
        
    * `check_script` (string)
    * `problem_seed` (int)
    * `student_submission` (string)
    * `expect_val` (string)"""

    # Seed the PRNG to get repeatable outputs
    random.seed(seed)

    # Create a dict to store the inputs
    inputs = {}

    # Fill in the check function with a random string
    comment_str = random_string()
    script = TEST_SCRIPT_TEMPLATE.format(comment_str)
    inputs['check_script'] = script

    # Random problem seed
    inputs['problem_seed'] = random.randint(0, 100000)

    # Random student submission string
    inputs['student_submission'] = random_string()

    # Expected value
    inputs['expect_val'] = random_string()

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

XML_FACTORY = CustomResponseXMLFactory()
def execute_test(check_script="", problem_seed=1, 
                 student_submission="", expect_val=1):
    """ Execute the test using input arguments.
    Returns `(did_raise_error, description)` tuple, where
    `raised_error` is a bool indicating that an unexpected error
    occurred and `description` is a string describing the error """

    # Build the problem XML
    problem_xml = XML_FACTORY.build_xml(script=check_script, cfn="check_func", expect=expect_val)

    # Create the problem
    problem = lcp.LoncapaProblem(problem_xml, '1', state=None,
                                 seed=problem_seed, system=system_mock())

    # Submit an answer and try to grade the problem
    answers = {'1_2_1': student_submission}

    try:
        problem.grade_answers(answers)

    except (StudentInputError, ResponseError, LoncapaProblemError):
        # Ignore expected, capa-specific errors
        return (False, None)

    except:
        # Report all other exceptions
        return (True, traceback.format_exc())

    else:
        return (False, None)

def run_fuzz_tests():
    """ Randomize student submission, check function, and hint function
    to see if we can break CustomResponse """

    iteration_count = 0

    while True:
        try:
            # Choose a random seed for this test run
            seed = random.randint(0, 2**16)

            # Generate random inputs
            inputs = generate_random_inputs(seed)

            # Execute the test and see if we get an unexpected exception
            (did_raise_error, description) = execute_test(inputs)

            # Record the error, if we got one
            if did_raise_error:
                print "ERROR {0}: {1}".format(seed, description)

            # Print a status update every 100 iterations
            iteration_count += 1
            if iteration_count % 100 == 0:
                print "."

        except KeyboardInterrupt:
            print "Stopping tests..."
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

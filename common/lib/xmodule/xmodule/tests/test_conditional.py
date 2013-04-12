
import json
#from path import path
#import unittest
from fs.memoryfs import MemoryFS

#from lxml import etree
from mock import Mock, patch
#from collections import defaultdict

#from xmodule.x_module import XMLParsingSystem, XModuleDescriptor
#from xmodule.xml_module import is_pointer_tag
#from xmodule.errortracker import make_error_tracker
from xmodule.modulestore import Location
from xmodule.modulestore.xml import ImportSystem, XMLModuleStore
#from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from capa.tests.response_xml_factory import OptionResponseXMLFactory
import xmodule.modulestore.django
#from .test_export import DATA_DIR

ORG = 'test_org'
COURSE = 'conditional'      # name of directory with course data

from . import test_system


class DummySystem(ImportSystem):

    @patch('xmodule.modulestore.xml.OSFS', lambda dir: MemoryFS())
    def __init__(self, load_error_modules):

        xmlstore = XMLModuleStore("data_dir", course_dirs=[], load_error_modules=load_error_modules)
        course_id = "/".join([ORG, COURSE, 'test_run'])
        course_dir = "test_dir"
        policy = {}
        error_tracker = Mock()
        parent_tracker = Mock()

        super(DummySystem, self).__init__(
            xmlstore,
            course_id,
            course_dir,
            policy,
            error_tracker,
            parent_tracker,
            load_error_modules=load_error_modules,
        )

    def render_template(self, template, context):
        raise Exception("Shouldn't be called")

# Try to see if this will work with a setting in the test profile,
# instead of overriding it with a different definition.
# @override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class ConditionalModuleTest(ModuleStoreTestCase):

    @staticmethod
    def get_system(load_error_modules=True):
        '''Get a dummy system'''
        return DummySystem(load_error_modules)

#    def setUp(self):
#        self.test_system = test_system()

#    def get_course(self, name):
#        """Get a test course by directory name.  If there's more than one, error."""
#        print "Importing {0}".format(name)
#
#        modulestore = XMLModuleStore(DATA_DIR, course_dirs=[name])
#        courses = modulestore.get_courses()
#        self.modulestore = modulestore
#        self.assertEquals(len(courses), 1)
#        return courses[0]

    def create_course(self):
        self.course = CourseFactory.create(org='HarvardX', number='ER22x')

        # Add a chapter to the course
        chapter = ItemFactory.create(parent_location=self.course.location)

        # add a sequence to the course to which the problem and conditional can be added
        self.section = ItemFactory.create(parent_location=chapter.location,
                                          template='i4x://edx/templates/sequential/Empty')

        # add a problem
        factory_dict = {'question_text': 'The correct answer is Option 2',
                        'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
                        'correct_option': 'Option 2'}
        problem_xml = OptionResponseXMLFactory().build_xml(**factory_dict)
        self.problem = ItemFactory.create(parent_location=self.section.location,
                                          template='i4x://edx/templates/problem/Blank_Common_Problem',
                                          display_name='choiceprob',
                                          data=problem_xml)
        # and add the conditional that depends on it
        # TODO: get sources arg from location of problem above
        conditional_xml = '<conditional attempted="True" sources="i4x://HarvardX/ER22x/problem/choiceprob"/>'
        self.conditional = ItemFactory.create(parent_location=self.section.location,
#                                              template='i4x://edx/templates/default/Empty',
                                              template='i4x://edx/templates/html/Blank_HTML_Page',
                                              category='conditional',
                                              display_name='condone',
                                              data=conditional_xml)

        # and something exposed when the condition is met:
        self.secret = ItemFactory.create(parent_location=self.conditional.location,
                                         template='i4x://edx/templates/html/Blank_HTML_Page',
                                         display_name='secret_page',
                                         # TODO: figure out which...
#                                         data='<html display_name="Secret Page"><p>This is a secret!</p></html>')
                                         data='<p>This is a secret!</p>')


    def test_conditional_module(self):
        """Make sure that conditional module works"""

        print "Starting import"
        self.test_system = test_system()
#        course = self.get_course('conditional_and_poll')
        self.create_course()

        print "Course: ", self.course
        print "id: ", self.course.id

        def inner_get_module(descriptor):
            if isinstance(descriptor, Location):
                location = descriptor
#                descriptor = self.modulestore.get_instance(self.course.id, location, depth=None)
                descriptor = xmodule.modulestore.django.modulestore().get_instance(self.course.id, location, depth=None)
            location = descriptor.location
            return descriptor.xmodule(self.test_system)

        # edx - HarvardX
        # cond_test - ER22x
        location = Location(["i4x", "HarvardX", "ER22x", "conditional", "condone"])

        def replace_urls(text, staticfiles_prefix=None, replace_prefix='/static/', course_namespace=None):
            return text
        self.test_system.replace_urls = replace_urls
        self.test_system.get_module = inner_get_module

        module = inner_get_module(location)
        print "module: ", module
        print "module.conditions_map: ", module.conditions_map
        print "module children: ", module.get_children()
        print "module display items (children): ", module.get_display_items()

        html = module.get_html()
        print "html type: ", type(html)
        print "html: ", html
        html_expect = "{'ajax_url': 'courses/course_id/modx/a_location', 'element_id': 'i4x-HarvardX-ER22x-conditional-condone', 'id': 'i4x://HarvardX/ER22x/conditional/condone', 'depends': 'i4x-HarvardX-ER22x-problem-choiceprob'}"
        self.assertEqual(html, html_expect)

        gdi = module.get_display_items()
        print "gdi=", gdi

        ajax = json.loads(module.handle_ajax('', ''))
        print "ajax: ", ajax
        html = ajax['html']
        self.assertFalse(any(['This is a secret' in item for item in html]))
        self.assertEquals(module.get_icon_class(), "test")

        # now change state of the capa problem to make it completed
        inner_get_module(Location('i4x://HarvardX/ER22x/problem/choiceprob')).attempts = 1

        ajax = json.loads(module.handle_ajax('', ''))
        print "post-attempt ajax: ", ajax
        html = ajax['html']
        self.assertTrue(any(['This is a secret' in item for item in html]))
        self.assertEquals(module.get_icon_class(), "test")


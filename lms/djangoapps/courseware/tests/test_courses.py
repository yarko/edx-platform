from django.test import TestCase
from courseware import courses
from mock import MagicMock

from collections import defaultdict
from fs.errors import ResourceNotFoundError
from functools import wraps
import logging

from path import path
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.utils import override_settings
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from static_replace import replace_urls, try_staticfiles_lookup
from courseware.access import has_access
import branding

def xml_store_config(data_dir):
    return {
    'default': {
        'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
        'OPTIONS': {
            'data_dir': data_dir,
            'default_class': 'xmodule.hidden_module.HiddenDescriptor',
        }
    }
}

TEST_DATA_DIR = settings.COMMON_TEST_DATA_ROOT
TEST_DATA_XML_MODULESTORE = xml_store_config(TEST_DATA_DIR)

@override_settings(MODULESTORE=TEST_DATA_XML_MODULESTORE)
class CoursesTests(TestCase):
	def setUp(self):
		self._MODULESTORES = {}
		self.course_name = 'edX/toy/2012_Fall'
		self.toy_course = modulestore().get_course('edX/toy/2012_Fall')

	def test_get_course_by_id(self):
		self.test_course_id = "edX/toy/2012_Fall"
		# print modulestore().get_instance(test_course_id, Location('i4x', 'edx', 'toy', 'course', '2012_Fall'))
		self.assertEqual(courses.get_course_by_id(self.test_course_id),modulestore().get_instance(self.test_course_id, Location('i4x', 'edX', 'toy', 'course', '2012_Fall'), None))
		

	def test_get_course_by_id2(self):
		self.assertRaisesRegexp(Http404,"Course not found.", courses.get_course_by_id,"meow/toy/hello")
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

from xmodule.course_module import CourseDescriptor
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from static_replace import replace_urls, try_staticfiles_lookup
from courseware.access import has_access
import branding

class CoursesTests(TestCase):

	def test_get_course_by_id(self):
		test_course_id = "edx/toy/2012_Fall"
		print modulestore().get_instance(test_course_id, Location('i4x', 'edx', 'toy', 'course', '2012_Fall'))
		self.assertEqual(courses.get_course_by_id(test_course_id),modulestore().get_instance(test_course_id, Location('i4x', 'edx', 'toy', 'course', '2012_Fall')))
		# comment
		# comment2

	def test_get_course_by_id2(self):
		self.assertEqual(courses.get_course_by_id("meow/toy/hello"), Http404("Course not found."))
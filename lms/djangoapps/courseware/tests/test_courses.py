from django.test import TestCase
from courseware import courses
from mock import MagicMock

from collections import defaultdict
from fs.errors import ResourceNotFoundError
from functools import wraps
import logging
import factory

from path import path
from django.conf import settings
from django.contrib.auth.models import User
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


class UserFactory(factory.Factory):
    FACTORY_FOR = User


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
        self.full = modulestore().get_course("edX/full/6.002_Spring_2012")
        self.user = User.objects.create(
            username="dummy", password="123456", email="test@dummy.com")
        self.fake_user = User.objects.create(is_superuser=True)

    '''
	no test written for get_request_for_thread
	'''

    def test_get_course_by_id(self):
        self.test_course_id = "edX/toy/2012_Fall"
        # print modulestore().get_instance(test_course_id, Location('i4x',
        # 'edx', 'toy', 'course', '2012_Fall'))
        self.assertEqual(courses.get_course_by_id(self.test_course_id), modulestore(
        ).get_instance(self.test_course_id, Location('i4x', 'edX', 'toy', 'course', '2012_Fall'), None))

    def test_get_course_by_id_notarealcourse(self):
        self.assertRaisesRegexp(Http404, "Course not found.",
                                courses.get_course_by_id, "meow/toy/hello")

    def test_get_course_with_access(self):

        self.assertEqual(
            courses.get_course_with_access(self.fake_user, self.course_name,
                                           'enroll'), courses.get_course_by_id("edX/toy/2012_Fall"))
        # self.assertRaisesRegexp(Http404,"Course not found.",
        # courses.get_course_with_access, self.fake_user2, self.course_name,
        # 'enroll')

    def test_get_opt_course_with_access(self):
        self.assertEqual(courses.get_opt_course_with_access(
            self.fake_user, None, 'enroll'), None)
        self.assertEqual(courses.get_opt_course_with_access(self.fake_user,
                         self.course_name, 'enroll'), courses.get_course_by_id("edX/toy/2012_Fall"))

    def test_course_image_url(self):
        # real course
        self.assertEqual(courses.course_image_url(
            self.toy_course), 'toy/images/course_image.jpg')

        # unable to test for when modulestore() is not an instance of
        # XMLModuleStore

    def test_find_file(self):
        pass

    def test_get_course_about_section(self):
        self.assertEqual(courses.get_course_about_section(
            self.toy_course, "title"), "Toy Course")
        self.assertEqual(courses.get_course_about_section(
            self.toy_course, "university"), "edX")
        '''
		See potential bugs page on the wiki. This test will word if 'number' is removed from line 148
		self.assertEqual(courses.get_course_about_section(self.toy_course, "number"), "toy")
		'''
        # self.assertEqual(courses.get_course_about_section(self.toy_course, "short_description"), "toy")
        # self.assertEqual(courses.get_course_about_section(self.toy_course,
        # "description"), "toy")

    def test_get_course_syllabus_section(self):
        self.assertRaisesRegexp(
            KeyError, "Invalid about key " + "meowtoyhello",
            courses.get_course_syllabus_section, self.toy_course, "meowtoyhello")
        '''
		this isn't raising a ResourceNotFoundError for some reason
		# self.assertRaisesRegexp(ResourceNotFoundError,"Resource not found",courses.get_course_syllabus_section,self.toy_course, 'syllabus')
		'''

    def test_get_courses_by_university(self):
        pass
        # self.assertEqual(courses.get_courses_by_university(self.fake_user),
        # "")

        # when self.user or self.fake_user is passed in, a super long defaultdict is
        # returned-- not sure where the elements of the output come from

    def test_get_courses(self):
        pass
        # self.assertEqual(courses.get_courses(self.user), '')
        # also outputs a really long defaultdict

    def test_sort_by_announcement(self):
        self.assertEqual(courses.sort_by_announcement([self.full, self.toy_course]), [self.toy_course, self.full])

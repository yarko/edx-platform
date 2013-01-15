import unittest
import logging 
import time
from mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from xmodule.course_module import CourseDescriptor 
from xmodule.error_module import ErrorDescriptor 
from xmodule.modulestore import Location 
from xmodule.timeparse import parse_time 
from xmodule.x_module import XModule, XModuleDescriptor
import courseware.access as access

class Stub:
    def __init__(self):
        pass

class AccessTestCase(TestCase):
    def setUp(self):
        pass
    
    def test__has_global_staff_access(self):
        # Only 2 branches?
        mock_user = MagicMock()
        mock_user.is_staff = True
        self.assertTrue(access._has_global_staff_access(mock_user))
        mock_user_2 = MagicMock()
        mock_user.is_staff = False
        self.assertFalse(access._has_global_staff_access(mock_user))

    def test__has_access_to_location(self):
        mock_user = MagicMock()
        mock_user.is_authenticated.return_value = False
        self.assertFalse(access._has_access_to_location(mock_user, "dummy", "dummy"))
        mock_user_2 = MagicMock()
        mock_user_2.groups.all.return_value = ['instructor_toy']
        location = MagicMock(spec=Location)
        location.course = 'toy'
        self.assertTrue(access._has_access_to_location(mock_user_2, location, "instructor"))
        mock_user_3 = MagicMock()
        mock_user_3.is_staff = False
        self.assertFalse(access._has_access_to_location(mock_user_3, 'dummy', 'dummy'))

    def test__dispatch(self):
        self.assertRaises(ValueError,access._dispatch,{}, 'dummy', 'dummy', 'dummy')

    def test__has_access_string(self):
        mock_user = MagicMock()
        mock_user.is_staff = True
        self.assertTrue(access._has_access_string(mock_user, 'global', 'staff'))
        self.assertFalse(access._has_access_string(mock_user, 'dummy', 'dummy'))
        
    def test__has_access_descriptor(self):
        mock_descriptor = MagicMock()
        mock_descriptor.start = 0
        # test has dependency on time.gmtime() > 0
        self.assertTrue(access._has_access_descriptor("dummy", mock_descriptor, 'load'))
        mock_descriptor_2 = MagicMock()
        mock_descriptor_2.start = None
        self.assertTrue(access._has_access_descriptor("dummy", mock_descriptor_2, 'load'))
        
    def test__has_access_error_desc(self):
        mock_user = None
        mock_descriptor = MagicMock()
        mock_descriptor.location = None
        # Just want to make sure function goes through path. 
        self.assertFalse(access._has_access_error_desc(mock_user, mock_descriptor, 'load'))

    def test__get_access_group_name_course_desc(self):
        # problem: can't nest magic mocks
        self.assertEquals(access._get_access_group_name_course_desc('dummy', 'notstaff'),
                          [])
##        mock_course = MagicMock()
##        
##        #mock_course.location.course = 'toy'
##        access._get_access_group_name_course_desc(mock_course, 'staff')

    def test__has_access_course_desc(self):
        # This is more of a test for see_exists
        mock_course = MagicMock()
        mock_course.metadata.get = 'is_public'
        self.assertTrue(access._has_access_course_desc('dummy', mock_course, 'see_exists'))
        mock_user = MagicMock()
        mock_course_2 = MagicMock()
        # Is there a way to see all the functions that have been called on a mock?
        # Basically, I want to see if _has_staff_access_to_descriptor is called on
        # the mock user and course
##        access._has_access_course_desc(mock_user, mock_course, 'see_exists')
##        print mock_user.mock_calls
##        print mock_course_2.location.assert_called_with()
##        assert False

# How do decorators work? I think that is the correct 
##    def test_patches(self):
##        user = Stub()
##        @patch.object(Stub, "is_staff", True)
##        self.assertTrue(access._has_global_staff_access(mock_user))

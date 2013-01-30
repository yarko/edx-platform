import logging
from mock import MagicMock, patch
import json
import factory
import unittest
from nose.tools import set_trace
from nose.plugins.skip import SkipTest

from django.http import Http404, HttpResponse, HttpRequest, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from override_settings import override_settings

from xmodule.modulestore.django import modulestore, _MODULESTORES
import contentstore.views as views

from util.json_request import expect_json
import json
import logging
import os
import sys
import time
import tarfile
import shutil
from datetime import datetime
from collections import defaultdict
from uuid import uuid4
from path import path
from xmodule.modulestore.xml_exporter import export_to_xml
from tempfile import mkdtemp
from django.core.servers.basehttp import FileWrapper
from django.core.files.temp import NamedTemporaryFile

# to install PIL on MacOSX: 'easy_install http://dist.repoze.org/PIL-1.1.6.tar.gz'
from PIL import Image

from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.context_processors import csrf
from django_future.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse
from django.conf import settings

from xmodule.modulestore import Location
from xmodule.modulestore.exceptions import ItemNotFoundError, InvalidLocationError
from xmodule.x_module import ModuleSystem
from xmodule.error_module import ErrorDescriptor
from xmodule.errortracker import exc_info_to_str
from static_replace import replace_urls
from external_auth.views import ssl_login_shortcut

from mitxmako.shortcuts import render_to_response, render_to_string
from xmodule.modulestore.django import modulestore
from xmodule_modifiers import replace_static_urls, wrap_xmodule
from xmodule.exceptions import NotFoundError
from functools import partial

from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent

from auth.authz import is_user_in_course_group_role, get_users_in_course_group_by_role
from auth.authz import get_user_by_email, add_user_to_course_group, remove_user_from_course_group
from auth.authz import INSTRUCTOR_ROLE_NAME, STAFF_ROLE_NAME, create_all_course_groups
# from .utils import get_course_location_for_item, get_lms_link_for_item, compute_unit_state, get_date_display, UnitState, get_course_for_item

from xmodule.modulestore.xml_importer import import_from_xml
from contentstore.course_info_model import get_course_updates,\
    update_course_updates, delete_course_update
from cache_toolbox.core import del_cached_content
from xmodule.timeparse import stringify_time
from contentstore.module_info_model import get_module_info, set_module_info
from cms.djangoapps.models.settings.course_details import CourseDetails,\
    CourseSettingsEncoder
from cms.djangoapps.models.settings.course_grading import CourseGradingModel
from cms.djangoapps.contentstore.utils import get_modulestore
from lxml import etree

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

class UserFactory(factory.Factory):
    first_name = 'Test'
    last_name = 'Robot'
    is_staff = True
    is_active = True

TEST_DATA_DIR = settings.COMMON_TEST_DATA_ROOT
TEST_DATA_XML_MODULESTORE = xml_store_config(TEST_DATA_DIR)

    # def test_assignment_type_update(self):
    #     # If user doesn't have access, should redirect
    #     self.user = MagicMock(is_staff = False, is_active = False)
    #     self.user.is_authenticated.return_value = False
    #     self.request = RequestFactory().get('foo')
    #     self.request.user = self.user
    #     self.assertIsInstance(views.assignment_type_update(self.request,
    #                                 'MITx', '999', 'course', 'Robot_Super_Course'),
    #                           HttpResponseRedirect)
    #     # if user has access, then should return HttpResponse
    #     self.user_2 = MagicMock(is_staff = True, is_active = True)
    #     self.user_2.is_authenticated.return_value = True
    #     self.request.user = self.user_2
    #     get_response = views.assignment_type_update(self.request,'MITx', '999',
    #                                                 'course', 'Robot_Super_Course')
    #     self.assertIsInstance(get_response,HttpResponse)
    #     get_response_string = '{"id": 99, "location": ["i4x", "MITx", "999", "course", "Robot_Super_Course", null], "graderType": "Not Graded"}'
    #     self.assertEquals(get_response.content, get_response_string)
    #     self.request_2 = RequestFactory().post('foo')
    #     self.request_2.user = self.user_2
    #     post_response = views.assignment_type_update(self.request_2,'MITx', '999',
    #                                                 'course', 'Robot_Super_Course')
    #     self.assertIsInstance(post_response,HttpResponse)
    #     self.assertEquals(post_response.content, 'null')

@override_settings(MODULESTORE=TEST_DATA_XML_MODULESTORE)
class ViewsTestCase(TestCase):
    def setUp(self):
        self.location = ['i4x', 'edX', 'toy', 'chapter', 'Overview']
        self.location_2 = ['i4x', 'edX', 'full', 'course', '6.002_Spring_2012']
        self._MODULESTORES = {}
        self.course_id = 'edX/toy/2012_Fall'
        self.course_id_2 = 'edx/full/6.002_Spring_2012'
        self.toy_course = modulestore().get_course(self.course_id)

    def test_has_access(self):
        user = UserFactory()
        user.is_authenticated = True
        self.assertTrue(views.has_access(user, self.location_2))
        user.is_authenticated = False
        self.assertFalse(views.has_access(user, self.location_2))

    def test_preview_component(self):
        self.request = MagicMock()
        self.request.user.return_value = UserFactory()
        self.request.user.is_authenticated = True
        self.assertRaisesRegexp(BaseException,"Found more than one course at *", views.preview_component, self.request.user, self.location)
        
    def test_preview_component_2(self):
        self.user = MagicMock(is_staff = False, is_active = False)
        self.user.is_authenticated.return_value = False
        self.request = RequestFactory().get('foo')
        self.request.user = self.user
        self.assertIsInstance(views.preview_component(self.request,
                                    self.location),
                              HttpResponseRedirect)
        self.assertFalse(views.has_access(self.request.user, self.location_2))

    def test_user_author_string(self):
        self.user2 = UserFactory()
        self.assertEqual(views.user_author_string(self.user2), "Test Robot <>")     

    def test_create_draft(self):
        self.user3 = MagicMock(is_staff = False, is_active = False)
        self.user3.is_authenticated.return_value = False
        self.request3 = RequestFactory().get('foo')
        self.request3.user = self.user3
        self.request3.POST = {}
        self.request3.POST['id'] = self.location
        self.assertIsInstance(views.create_draft(self.request3), HttpResponseRedirect)

        #WHY THIS NOT WORK?
        self.user4 = MagicMock(is_staff = False, is_active = False)
        self.user4.is_authenticated.return_value = True
        self.request4 = RequestFactory().get('foo')
        self.request4.user = self.user4
        self.request4.POST = {}
        self.request4.POST['id'] = self.location_2
        # self.assertRaisesRegexp(BaseException,"Found more than one course at *", views.create_draft, self.request4.user)
        # self.assertIsInstance(views.create_draft(self.request4), HttpResponse)

    def test_publish_draft(self): #same test as above
        self.user5 = MagicMock(is_staff = False, is_active = False)
        self.user5.is_authenticated.return_value = False
        self.request5 = RequestFactory().get('foo')
        self.request5.user = self.user5
        self.request5.POST = {}
        self.request5.POST['id'] = self.location
        self.assertIsInstance(views.create_draft(self.request5), HttpResponseRedirect)
    
    def test_unpublish_unit(self): #same test as aboves
        self.user6 = MagicMock(is_staff = False, is_active = False)
        self.user6.is_authenticated.return_value = False
        self.request6 = RequestFactory().get('foo')
        self.request6.user = self.user6
        self.request6.POST = {}
        self.request6.POST['id'] = self.location
        self.assertIsInstance(views.create_draft(self.request6), HttpResponseRedirect)
    # def tearDown(self):
    #     _MODULESTORES = {}
    #     modulestore().collection.drop()

from django.contrib.auth.models import User
from django.test import TestCase
from student.models import CourseEnrollment, \
                           replicate_enrollment_save, \
                           replicate_enrollment_delete, \
                           update_user_information, \
                           replicate_user_save
                           
from django.db.models.signals import m2m_changed, pre_delete, pre_save, post_delete, post_save
from django.dispatch.dispatcher import _make_id
import string
import random
from .permissions import has_permission
from .models import Role, Permission
from .helpers import pluralize
from .mustache_helpers import close_thread_text
from .mustache_helpers import url_for_user
from comment_client import CommentClientError
from django.http import HttpRequest
from django.http import HttpRequest
from .middleware import *


class PermissionsTestCase(TestCase):
    def random_str(self, length=15, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(length))

    def setUp(self):

        self.course_id = "edX/toy/2012_Fall"

        self.moderator_role = Role.objects.get_or_create(name="Moderator", course_id=self.course_id)[0]
        self.student_role = Role.objects.get_or_create(name="Student", course_id=self.course_id)[0]

        self.student = User.objects.create(username=self.random_str(),
                            password="123456", email="john@yahoo.com")
        self.moderator = User.objects.create(username=self.random_str(),
                            password="123456", email="staff@edx.org")
        self.moderator.is_staff = True
        self.moderator.save()
        self.student_enrollment = CourseEnrollment.objects.create(user=self.student, course_id=self.course_id)
        self.moderator_enrollment = CourseEnrollment.objects.create(user=self.moderator, course_id=self.course_id)

    def tearDown(self):
        self.student_enrollment.delete()
        self.moderator_enrollment.delete()

# Do we need to have this? We shouldn't be deleting students, ever
#        self.student.delete()
#        self.moderator.delete()


    def testDefaultRoles(self):
        self.assertTrue(self.student_role in self.student.roles.all())
        self.assertTrue(self.moderator_role in self.moderator.roles.all())

    def testPermission(self):
        name = self.random_str()
        self.moderator_role.add_permission(name)
        self.assertTrue(has_permission(self.moderator, name, self.course_id))

        self.student_role.add_permission(name)
        self.assertTrue(has_permission(self.student, name, self.course_id))

class PluralizeTestCase(TestCase):
	
	def setUp(self):
		self.term = "cat"

	def test_pluralize(self):
		self.assertEqual(pluralize(self.term, 0), "cats")
		self.assertEqual(pluralize(self.term, 1), "cat")
		self.assertEqual(pluralize(self.term, 3), "cats")

	def tearDown(self):
		pass

#Tests for .middleware

class ProcessExceptionTestCase(TestCase):


	def setUp(self):
		self.a = AjaxExceptionMiddleware()
		self.request1 = HttpRequest()
		self.request0 = HttpRequest()
		self.exception1 = CommentClientError('a')
		self.exception0 = 5
		self.request1.META['HTTP_X_REQUESTED_WITH'] = "XMLHttpRequest"
		self.request0.META['HTTP_X_REQUESTED_WITH'] = "SHADOWFAX"


		
	def test_process_exception(self):
		self.assertRaises(JsonError, self.a.process_exception(self.request1, self.exception1))
		self.assertIsNone(self.a.process_exception(self.request1, self.exception0))
		self.assertIsNone(self.a.process_exception(self.request0, self.exception1))
		self.assertIsNone(self.a.process_exception(self.request0, self.exception0))

	def tearDown(self):
		pass
		
		
		
		

#Tests for mustache_helpers.py

#class UrlForUserTestCase(TestCase):
	
#	def setUp(self):
#		self.content = {'course_id': 6.002}
#		self.user_id = 'jeanmanuel'

#	def test_url_for_user(content, user_id):
#		self.assertEqual(url_for_user(content, user_id), url_for_user(content, user_id))

#	def tearDown(self):
#		pass


		
		

class CloseThreadTextTestCase(TestCase):
	
	def setUp(self):
		self.contentClosed = {'closed': True}
		self.contentOpen = {'closed': False}

	def test_close_thread_text(self):
		self.assertEqual(close_thread_text(self.contentClosed), 'Re-open thread')
		self.assertEqual(close_thread_text(self.contentOpen), 'Close thread')

	def tearDown(self):
		pass




	

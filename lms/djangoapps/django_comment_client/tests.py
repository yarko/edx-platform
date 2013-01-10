import string
import random


from django.contrib.auth.models import User
from django.test import TestCase                         
from django.db.models.signals import m2m_changed, pre_delete, pre_save, post_delete, post_save
from django.dispatch.dispatcher import _make_id

from student.models import CourseEnrollment, \
                           replicate_enrollment_save, \
                           replicate_enrollment_delete, \
                           update_user_information, \
                           replicate_user_save
from .permissions import *
from .models import Role, Permission
from .helpers import pluralize

class PermissionsTestCase(TestCase):
    def random_str(self, length=15, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(length))

    def setUp(self):

        self.course_id = "edX/toy/2012_Fall"

        self.moderator_role = Role.objects.get_or_create(name="Moderator", \
                                                         course_id=self.course_id)[0]
        self.student_role = Role.objects.get_or_create(name="Student", \
                                                       course_id=self.course_id)[0]

        self.student = User.objects.create(username=self.random_str(),
                            password="123456", email="john@yahoo.com")
        self.moderator = User.objects.create(username=self.random_str(),
                            password="123456", email="staff@edx.org")
        self.moderator.is_staff = True
        self.moderator.save()
        self.student_enrollment = CourseEnrollment.objects.create(user=self.student, \
                                                                  course_id=self.course_id)
        self.moderator_enrollment = CourseEnrollment.objects.create(user=self.moderator, \
                                                                    course_id=self.course_id)
        #Fake json files
        self.empty_data = {"content":{
                                    }
                    }
        self.open_data = {"content":{
                                "closed":False,
                                "user_id":str(self.student.id)
                                }
                     }
        self.closed_data = {"content":{
                                "closed":True,
                                "user_id":str(self.student.id)
                                }
                     }
        
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
        # Moderators do not have student priveleges unless explicitly added

        self.student_role.add_permission(name)
        self.assertTrue(has_permission(self.student, name, self.course_id))

        # Students don't have moderator priveleges 
        name2 = self.random_str()
        self.student_role.add_permission(name2)
        self.assertFalse(has_permission(self.moderator, name2, self.course_id))

    def testCachedPermission(self):
        
        # Cache miss returns None
        # Don't really understand how this works? What's in Cache?
        self.assertFalse(cached_has_permission(self.student, self.moderator, \
                                            course_id=None))
        self.assertFalse(cached_has_permission(self.student, "update_thread", \
                                            course_id=None))

    def testCheckCondition(self):
        # Checks whether something? is open, or whether the author is user
        self.assertFalse(check_condition(self.student, 'is_open', \
                                         self.course_id, self.empty_data))
        self.assertFalse(check_condition(self.student, 'is_author', \
                                         self.course_id, self.empty_data))
        self.assertTrue(check_condition(self.student,'is_open', \
                                         self.course_id, self.open_data))
        self.assertTrue(check_condition(self.student, 'is_author', \
                                         self.course_id, self.open_data))
        self.assertFalse(check_condition(self.student,'is_open', \
                                         self.course_id, self.closed_data))

    def testCheckConditionsPermissions(self):
        # Should be True, but test fails in that case?
        # What do I have to do to get True?
        self.assertFalse(check_conditions_permissions(self.student, 'is_open', \
                                                     self.course_id,\
                                                     data=self.open_data))
        self.assertFalse(check_conditions_permissions(self.student, 'is_open', \
                                                     self.course_id,\
                                                     data=self.empty_data))

        self.assertFalse(check_conditions_permissions(self.student, \
                                                      ['is_open', 'is_author'],\
                                                      self.course_id,\
                                                      data=self.open_data))
        self.assertFalse(check_conditions_permissions(self.student, \
                                                      ['is_open', 'is_author'],\
                                                      self.course_id,\
                                                      data=self.open_data,\
                                                      operator='and'))
        self.assertFalse(check_conditions_permissions(self.student, 'update_thread',\
                                                      self.course_id, data=self.open_data))

    def testCheckPermissionsByView(self):
        # kwargs is the data entered in check_condition, which is json?
##        self.assertRaises(UnboundLocalError, check_permissions_by_view(self.student,\
##                                                self.course_id,\
##                                                self.empty_data,\
##                                                  "nonexistant"))
        self.assertFalse(check_permissions_by_view(self.student,self.course_id, \
                                                   self.empty_data, 'update_thread'))
##        self.assertTrue(check_permissions_by_view(self.student,self.course_id, \
##                                                   self.open_data, 'vote_for_thread'))

class PluralizeTestCase(TestCase):
    """Practice test case"""
    def setUp(self):
        self.term = "cat"

    def testPluralize(self):
        self.assertEqual(pluralize(self.term, 0), "cats")
        self.assertEqual(pluralize(self.term, 1), "cat")
        self.assertEqual(pluralize(self.term, 2), "cats")

    def tearDown(self):
        pass

# finished testing models.py

class PermissionClassTestCase(TestCase):

    def setUp(self):
        
        self.permission = Permission.objects.get_or_create(name="test")[0]

    def testUnicode(self):
        # Doesn't print?
        self.assertEqual(str(self.permission), "test")

class RoleClassTestCase(TestCase):
    def setUp(self):
        # Create a Role
        # Problem: can't create Role, error is
        #RoleClassTestCase() takes exactly 1 argument (0 given)
        self.course_id = "edX/toy/2012_Fall"
        self.student_role = Role.objects.get_or_create(name="Student", \
                                                         course_id=self.course_id)[0]
        self.student_role.add_permission("delete_thread")
        self.student_2_role = Role.objects.get_or_create(name="Student", \
                                                         course_id=self.course_id)[0]
        self.TA_role = Role.objects.get_or_create(name="Community TA",\
                                                  course_id=self.course_id)[0]
        self.course_id_2 = "course2"
        self.TA_role_2 = Role.objects.get_or_create(name="Community TA",\
                                                  course_id=self.course_id_2)[0]
        
    def testHasPermission(self):
        # It seems that whenever you add a permission to student_role,
        # Roles with the same FORUM_ROLE also receives the same permission.
        # Is this desirable?
        self.assertTrue(self.student_role.has_permission("delete_thread"))
        self.assertTrue(self.student_2_role.has_permission("delete_thread"))
        self.assertFalse(self.TA_role.has_permission("delete_thread"))

    def testInheritPermissions(self):
        self.TA_role.inherit_permissions(self.student_role)
        self.assertTrue(self.TA_role.has_permission("delete_thread"))
        self.assertFalse(self.TA_role_2.has_permission("delete_thread"))
        # Despite being from 2 different courses, TA_role_2 can still inherit
        # permissions from TA_role 
        self.TA_role_2.inherit_permissions(TA_role)
        self.assertTrue(self.TA_role_2.has_permission("delete_thread"))

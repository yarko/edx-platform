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
from .utils import strip_none
from .utils import extract
from .utils import strip_blank
from .utils import merge_dict
from .utils import get_role_ids
from .utils import get_full_modules
from .utils import get_discussion_id_map
from xmodule.modulestore.django import modulestore

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

class UtilsTestCase(TestCase):
    def random_str(self, length=15, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(length)) 

    def setUp(self):
        self.dic1 = {}
        self.dic2 = {}
        self.dic2none = {}
        self.dic2blank = {}

        self.dic1["cats"] = "meow"
        self.dic1["dogs"] = "woof"
        self.dic1keys = ["cats", "dogs", "hamsters"]

        self.dic2["lions"] = "roar"
        self.dic2["ducks"] = "quack"
        
        self.dic2none["lions"] = "roar"
        self.dic2none["ducks"] = "quack"
        self.dic2none["seaweed"] = None

        self.dic2blank["lions"] = "roar"
        self.dic2blank["ducks"] = "quack"
        self.dic2blank["whales"] = ""   

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
        self.course = "6.006"

    def test_extract(self):
        test_extract_dic1 = {"cats": "meow", "dogs": "woof", "hamsters": None}
        self.assertEqual(extract(self.dic1, self.dic1keys), test_extract_dic1)

    def test_strip_none(self):
        self.assertEqual(strip_none(self.dic2none), self.dic2)

    def test_strip_blank(self):
        self.assertEqual(strip_blank(self.dic2blank), self.dic2)

    def test_merge_dic(self):
        self.dicMerge12 ={'cats': 'meow', 'dogs': 'woof','lions': 'roar','ducks': 'quack'}
        self.assertEqual(merge_dict(self.dic1, self.dic2), self.dicMerge12)

    def test_get_role_ids(self):
        self.assertEqual(get_role_ids(self.course_id), {u'Moderator': [2], u'Student': [1], 'Staff': [2]})

    def test_get_full_modules(self):
        _FULLMODULES = True
        self.assertTrue(get_full_modules())
        _FULLMODULES = False
        self.assertEqual(get_full_modules(), modulestore().modules)

    def test_get_discussion_id_map(self):
        _DISCUSSIONINFO = defaultdict({"6.006": False, "18.410": True})
        


from django.test import TestCase
from courseware import grades
from mock import MagicMock

# from __future__ import division

# import random
# import logging

# from collections import defaultdict
# from django.conf import settings
# from django.contrib.auth.models import User

# from models import StudentModuleCache
# from module_render import get_module, get_instance_module
from xmodule import graders
from xmodule.capa_module import CapaModule
from xmodule.course_module import CourseDescriptor
from xmodule.graders import Score
# from models import StudentModule

class test_grades(TestCase):

	def setUp(self):
		pass

	def test_yield_module_descendents(self):
		mock_module = MagicMock()
		a = MagicMock()
		b = MagicMock()
		c = MagicMock()
		z = MagicMock()
		y = MagicMock()
		mock_module.get_display_items.return_value = [a, b, c]
		a.get_display_items.return_value = [y, z]  
		b.get_display_items.return_value = []
		c.get_display_items.return_value = []
		z.get_display_items.return_value = []
		y.get_display_items.return_value = []
		dummy = list(grades.yield_module_descendents(mock_module))
		self.assertEqual(dummy, [a,z,y,b,c])

	def test_yield_dynamic_descriptor_descendents(self):
		descriptor_true_mock = MagicMock()
		a = MagicMock()
		b = MagicMock()
		b.has_dynamic_children.return_value = False
		b.get_children.return_value = 'b'
		c = MagicMock()
		c.has_dynamic_children.return_value = False
		c.get_children.return_value = 'c'
		e = MagicMock()
		e.has_dynamic_children.return_value = False
		e.get_children.return_value = None

		descriptor_true_mock.return_value = a
		descriptor_true_mock.has_dynamic_children.return_value = True
		module_creator_mock = MagicMock()
		module_mock = MagicMock()
		module_creator_mock(descriptor_true_mock).return_value = module_mock
		child_locations_mock = MagicMock()
		module_mock.get_children_locations.return_value = [b, c]
		print descriptor_true_mock.system.load_item(b)
		

		descriptor_true_mock.system.load_item(b).return_value = b
		descriptor_true_mock.system.load_item(c).return_value = c

		descriptor_false_mock = MagicMock()
		descriptor_false_mock.has_dynamic_children.return_value = False
		descriptor_false_mock.get_children.return_value = e

		true_descriptor_children_list = [descriptor_true_mock]
		self.assertEqual(list(grades.yield_dynamic_descriptor_descendents(descriptor_true_mock, module_creator_mock)),true_descriptor_children_list)					
		self.assertEqual(list(grades.yield_dynamic_descriptor_descendents(descriptor_false_mock, module_creator_mock)),[descriptor_false_mock])	


		



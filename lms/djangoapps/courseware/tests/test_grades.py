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

	def test_yield_module_descendents(self):
		
		dummy = list(grades.yield_module_descendents(mock_module))
		self.assertEqual(dummy, [a,z,y,b,c])

	def test_yield_dynamic_descriptor_descendents(self):
		descriptor_true_mock = MagicMock()
		a = MagicMock()
		b = MagicMock()
		c = MagicMock()
		d = MagicMock()
		e = MagicMock()
		f = MagicMock()
		g = MagicMock()
		h = MagicMock()
		i = MagicMock()
		descriptor_true_mock.return_value = [a, b ]
		get_dynamic_descriptor_children(a).return._value= [c, d]
		get_dynamic_descriptor_children(b).retunr_value = []
		get_dynamic_descriptor_children(c) = []
		get_dynamic_descriptor_children(d) = []
		descriptor_true_mock.has_dynamic_children.return_value = False
		
		descriptor_false_mock = MagicMock()
		descriptor_false_mock.return_value = [e, f ]
		get_dynamic_descriptor_children(e).return._value= [g, h]
		get_dynamic_descriptor_children(f).return_value = []
		get_dynamic_descriptor_children(g) = []
		get_dynamic_descriptor_children(h) = []
		descriptor_false_mock.has_dynamic_children.return_value = True
		module_creator_mock = MagicMock()
		module_mock = MagicMock()
		module_creator_mock(descriptor_true_mock).return_value = module_mock
		child_locations = ['locA', 'locB', 'locC']
		module_mock.get_children_locations.return_value = child_locations
		descriptor_true_mock.system.load_item('locA').return_value = ['A']
		descriptor_true_mock.system.load_item('locB').return_value = ['B']
		descriptor_true_mock.system.load_item('locC').return_value = ['C']
		descriptor_false_mock.get_children.return_value = "Descriptor with no\
														dynamic children"

		self.assertEqual(yield_dynamic_descriptor_descendents(descriptor_true_mock, module_creator_mock),)					



		



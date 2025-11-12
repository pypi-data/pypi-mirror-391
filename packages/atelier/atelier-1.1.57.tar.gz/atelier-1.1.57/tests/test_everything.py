# -*- coding: UTF-8 -*-

from atelier.test import TestCase


class BasicTests(TestCase):

    def test_01(self):
        self.assertEqual(1 + 1, 2)

    # the following test case should always be commented out
    # def test_fail_with_unicode_error(self):
    #     self.fail(u"Scheiße wa!")

    def test_utils(self):
        self.run_simple_doctests('atelier/utils.py')

    def test_sheller(self):
        self.run_simple_doctests('atelier/sheller.py')

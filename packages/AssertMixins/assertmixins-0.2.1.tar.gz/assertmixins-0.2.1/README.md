# A library of mixin classes containing assertion methods

Example of use:

    # -*- coding: utf-8 -*-
    import unittest, assert_mixins
    
    class SampleTestCase(unittest.TestCase, assert_mixins.ElementaryMixin):
        def test_thing_has_length_two(self):
            self.assertLength([3, 4], 2, msg="Length is different from two!")

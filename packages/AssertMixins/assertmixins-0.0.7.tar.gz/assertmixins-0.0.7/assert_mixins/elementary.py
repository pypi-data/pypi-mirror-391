# -*- coding: utf-8 -*-

class ElementaryMixin:
    """
    Elementary assertions, meaning:
     * Based on standard unittest assertions;
     * Or delivering better reporting;
     * Or with more generality.
    """
    def assertLength(self, collection, length, msg=None):
        """
        Asserts() that a collection has a given length.
            self        An object that must be duck-compatible with unittest.Testcase.
            collection  A collection whose length is to be asserted about.
            length      The expected length.
            msg         Same meaning as in other assertions.
        """
        self.assertEqual(len(collection), length, msg=msg or f"Collection length is not {length}: {collection}")

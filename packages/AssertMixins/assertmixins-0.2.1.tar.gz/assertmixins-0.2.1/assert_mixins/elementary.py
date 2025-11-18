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
    
    def assertPosixSuccess(self, exit_code, msg=None):
        """
        Asserts() that a given value represents a POSIX program success (i.e. it's a zero integer).
            self        An object that must be duck-compatible with unittest.Testcase.
            exit_code   A value to be asserted to be a zero.
        """
        self.assertEqual(exit_code, 0, msg=msg or f"Value {exit_code} does not represent a POSIX program success; it should be a 0 instead.")
    def assertPosixFailure(self, exit_code, msg=None):
        """
        Asserts() that a given value represents a POSIX program feilure (i.e. it's a non-zero integer).
            self        An object that must be duck-compatible with unittest.Testcase.
            exit_code   A value to be asserted to be a non-zero integer.
        """
        self.assertIsInstance(exit_code, int, msg=msg or f"Value {exit_code} is not an integer.")
        self.assertNotEqual(exit_code, 0, msg=msg or f"Value {exit_code} does not represent a POSIX program failure; it should be a non-0 integer instead.")

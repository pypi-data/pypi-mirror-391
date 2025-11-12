#!/usr/bin/env python
#
# Tests for LeanCheck itself.
#
# (C) 2023-2024  Rudy Matela
# Distributed under the LGPL v2.1 or later (see the file LICENSE)


import unittest
import itertools
from leancheck import Enumerator


def take(n, generator):
    """
    This function returns a list with the first _n_ elements of a generator.

    >>> take(3, [1,2,3,4,5,6])
    [1, 2, 3]

    >>> take(6, itertools.count())
    [0, 1, 2, 3, 4, 5]
    """
    return list(itertools.islice(generator, n))


class TestLeanCheck(unittest.TestCase):

    def assertEnum(self, typ, lst):
        self.assertEqual(take(6, Enumerator[typ]), lst)

    def test_constructor(self):
        e = Enumerator(lambda: ([x] for x in [3,1,3,3,7]))
        self.assertEqual(list(e), [3,1,3,3,7])
        self.assertEqual(list(e.tiers()), [[3],[1],[3],[3],[7]])
    
    def test_from_list(self):
        e = Enumerator.from_list([3,1,3,3,7])
        self.assertEqual(list(e), [3,1,3,3,7])

    def test_int(self):
        self.assertEnum(int, [0,1,2,3,4,5])
        self.assertEnum(list[int], [[], [0], [0, 0], [1], [0, 0, 0], [1, 0]])

    def test_bool(self):
        self.assertEnum(bool, [False,True])
        self.assertEnum(list[bool], [[], [False], [True], [False,False], [True,False], [False,True]])

    def test_tuple(self):
        self.assertEnum(tuple[int,int], [(0,0), (0,1), (1,0), (0,2), (1,1), (2,0)])
        self.assertEnum(tuple[int,int,int], [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), (0, 0, 2), (0, 1, 1)])
        self.assertEnum(tuple[bool,bool], [(False, False), (False, True), (True, False), (True, True)])

    def test_empty_product(self):
        e = Enumerator.product()
        self.assertEqual(list(e), [()])
        self.assertEqual(list(e.tiers()), [[()]])


if __name__ == '__main__':
    unittest.main()

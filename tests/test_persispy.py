#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import persispy
from persispy.points import box
import timeit as t
import doctest

"""
test_persispy
----------------------------------

Tests for `persispy` module.

from persispy import persispy


class TestPersispy(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass
"""


import persispy.points as pp
import persispy.weighted_simplicial_complex as wsc
import persispy.persistent_homology as pph
import numpy.random as npr
from persispy.hashing import HashPoint
from persispy.point_cloud import PointCloud

class TestPersistence(unittest.TestCase):

    def test_barcode(self):

        points = pp.sphere(200,1)
        weighted_graph = points.neighborhood_graph(.1,'subdivision')
        scl = wsc.sorted_clique_list(weighted_graph)
        wscomplex = wsc.wSimplicialComplex.from_clique_list(weighted_graph,
                                                            scl._cliques)

        ph = pph.PersistentHomology(wscomplex,4)

        ph.plot_bar_code(.1, gui=True)

class TestConnectedComponents(unittest.TestCase):

    def setUp(self):
        pc = box(20, seed=1991)
        self.ng = pc.neighborhood_graph(0.2)

    def test_time_cp(self):

        def wrapper():
            self.ng.connected_components()

        print("")
        print(".connected_components():   %f" % t.timeit(wrapper, number=10))

    def test_connected_components_equal_to(self):
        x = 5
        print(len(self.ng.connected_components()))
        self.assertEqual(len(self.ng.connected_components()), x)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(persispy))
    return tests


if __name__ == '__main__':
    testSuite = unittest.TestSuite()
    persispyDocTest = doctest.DocTestSuite(persispy.hashing)

    testSuite.addTest(persispyDocTest)
    unittest.TextTestRunner(verbosity=9).run(testSuite)

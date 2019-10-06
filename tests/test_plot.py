import unittest
import persispy
import doctest

from persispy.points import sphere
from persispy.plot import plot2d, plot3d

class TestPlot(unittest.TestCase):

    def setUp(self):

        self.pc = sphere(200)
        self.ng = self.pc.neighborhood_graph(.2)

    def test_3d_plot(self):

        plot3d(self.pc, gui=True)
        plot3d(self.ng, gui=True)

    def test_2d_plot(self):

        plot2d(self.pc, gui=True)
        plot2d(self.ng, shading_style="axes", gui=True)
        plot2d(self.ng, shading_style="component", gui=True)


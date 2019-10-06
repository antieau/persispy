import unittest
from persispy.phc import Intersect
from persispy.points import sphere
import timeit as t


class TestPHCPack(unittest.TestCase):

    def setUp(self):
        self.points = 500

    def test_sampling_points_2sphere(self):

        selection = "x^2 + y^2 + z^2 - 1"
        Intersect(eqn=selection, num_points=self.points, bounds=30)

    def test_time_sampling_points(self):

        def wrapper():
            sphere(self.points)

        def wrapper1():
            selection = "x^2 + y^2 + z^2 - 1"
            Intersect(eqn=selection, num_points=self.points)

        print("")
        print("sphere(): %f" % t.timeit(wrapper, number=3))
        print("phc():    %f" % t.timeit(wrapper1, number=3))

    def test_time_sampling_points_complex(self):

        def wrapper1():
            selection = "x^2 + y^2 + z^2 - 1"
            Intersect(eqn=selection,
                      num_points=self.points,
                      return_complex=True)

        print("")
#         print "sphere(): %f" % t.timeit(wrapper, number = 10)
        print("phc():    %f" % t.timeit(wrapper1, number=3))


if __name__ == '__main__':
    unittest.main(verbosity=9)

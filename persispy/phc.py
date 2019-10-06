"""
AUTHORS:

    - Daniel Etrata (2016-01)

Takes a variety of type string and, after solving intersections with phcpy,
returns a persispy point cloud. We must reject equations with with variables t,
e, E, i, I because their meanings are reserved.
"""

from string import ascii_letters, digits

import numpy as np

from persispy.hashing import HashPoint
from persispy.point_cloud import PointCloud

from phcpy.solver import total_degree_start_system, total_degree
from phcpy.trackers import track
from phcpy.solutions import strsol2dict  # points

DEBUG = False


class Intersect(object):
    """
    We take an equation that is, in general, of the form
    A*x^2 + B*x + C = 0 and return a PointCloud on that variety.
    """

    def __init__(self,
                 eqn,
                 num_points=1,
                 bounds=10,
                 return_complex=False,
                 coefficient_distribution='normal',
                 intersect_constant=False):
        self._bounds = bounds
        self._failure = num_points
        self._coefficient_distribution = coefficient_distribution
        self._intersect_constant = intersect_constant
        self.complex_threshold = 0.1
        self.eqn = eqn
        self.varlist, self.coefflist = parse(eqn)
        self.points = []

        if DEBUG:
            self.attempt = 0

#         self._startsystem, self._startsol = self._start_system()
        partition = 256
        i = 0
        while i < num_points // partition:
            self._startsystem, self._startsol = self._start_system()
            self.find_more_points(partition, return_complex)
            i = i + 1

        self._startsystem, self._startsol = self._start_system()
        self.find_more_points(num_points - len(self.points), return_complex)
        self.__call__()

    def degree(self):
        """
        We return the degree of the system.
        """
        return total_degree(self._system())

    def _system(self):
        """
        We construct a square system, where the number of variables is
        equal to the number of eqations. The resulting points are
        regular and bounded by the variety.
        """
        phceqn = self.eqn + ";"
        phcsystem = [phceqn]
        for _ in range(len(self.varlist) - 1):
            phcsystem.append(self._intersect())
        return phcsystem

    def _intersect(self):
        """
        We form intersects from the extracted terms. We return a plane
        with random coefficients to intersect the variety. The
        intersects must be of the same dimension as the variety to
        prevent a overdetermined system (which phc doesn't do nicely)
        """
        bounds = self._bounds
        coefficient_distribution = self._coefficient_distribution
        constant = self._intersect_constant

        if coefficient_distribution == 'rejection':
            def normalize(x):
                "Normalizes the point"
                return (1 / np.sqrt(sum(x * x))) * x
            randomlist = [None]
            while not all(randomlist):
                pt = 2 * np.random.random(size=len(self.varlist)) - 1
                if np.sqrt(sum(pt * pt)) <= 1:
                    randomlist = normalize(pt)
        if coefficient_distribution == 'normal':
            randomlist = np.random.normal(scale=bounds, size=len(self.varlist))
        elif coefficient_distribution == 'uniform':
            randomlist = np.random.uniform(high=bounds, low=0,
                                           size=len(self.varlist))
        intersect = []
        for i, var in enumerate(self.varlist):
            intersect.append(str(randomlist[i]) + " * " + var)
            if i < len(self.varlist) - 1:
                intersect.append(" + ")
            elif constant:
                intersect.append(" + " + str(randomlist[i]))
        intersect.append(";")
        intersect = "".join(intersect)
        return intersect

    def _start_system(self):
        """
        We first set up a start system so phcpy doesn't have to create
        a new one everytime.
        """
        phcsystem = self._system()
        startsystem, startsol = total_degree_start_system(phcsystem)
        return startsystem, startsol

    def find_more_points(self, num_points, return_complex=False):
        """
        We find additional points on the variety.
        """
        points = []
        failure = 0
        while(len(points) < num_points):
            phcsystem = self._system()
            phcsolutions = track(phcsystem, self._startsystem, self._startsol)

            #  Parsing the output of solutions
            for sol in phcsolutions:
                solutiondict = strsol2dict(sol)

                point = [solutiondict[variable] for variable in self.varlist]
                if return_complex:
                    points.append(tuple(point))
                else:
                    closeness = True
                    for component in point:
                        # choses the points we want
                        if self._is_close(component.imag) \
                                and self._in_bounds(component.real):
                            # sometimes phcpy gives more points than we
                            # ask, thus the additional check
                            if component == point[-1] \
                                    and closeness \
                                    and len(points) < num_points:
                                points.append(tuple(
                                    [component.real for component in point]))
                                assert len(points) <= num_points
                                failure = 0
                        else:
                            closeness = False
                            failure = failure + 1
            if self._failure <= failure:
                raise RuntimeError(
                    "equation has too many complex solutions in a row")

        self.points = points + self.points

    def _is_close(self, number):
        """
        We need to deal with the fact that PHC always returns complex solutions,
        as small as 10^-48, so the threshold cannot be 0.
        """
        epsilon = self.complex_threshold
        result = abs(number) <= epsilon
        return result

    def _in_bounds(self, number):
        """
        If we need to sample points on unbounded varieties, we check if the
        points are within a certain bound.
        """
        bounds = self._bounds
        if bounds and \
                -bounds <= number and number <= bounds:
            return True
        else:
            return False

    def __call__(self):
        cloudpoints = []
        i = 0
        for coord in self.points:
            cloudpoints.append(
                HashPoint(
                    np.array(
                        coord,
                        dtype=complex
                    ),
                    index=i
                )
            )
            i = i + 1
        self.pointcloud = PointCloud(cloudpoints)
        return self.pointcloud

    def __repr__(self):
        return self.points.__repr__()

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __getattr__(self, name):
        """
        We allow PointCloud methods to be called on the instance.
        """
        try:
            return getattr(self.pointcloud, name)
        except AttributeError:
            raise


def parse(eqn): #noqa - too many branches
    """
    We parse the equation string into phcpy input.
    """

    terms = eqn
    # Extracting terms from the target
    for operation in ["+", "-", "*", "**", "^"]:
        terms = terms.replace(operation, " ")
    terms = terms.strip(" ")
    varlist = []
    for term in terms:
        if term in ["e", "E", "i", "I", "t"]:
            raise RuntimeError("\"" + term + "\" is reserved. Please use a "
                               "different variable.")
        if not term.isdigit() and term.isalnum() and term not in varlist:
            varlist.append(term)
    varlist.sort()

    coeffs = eqn
    coeffs = coeffs.replace("-", "+")
    coeffs = coeffs.replace(" ", "")
    coeffs = coeffs.split("+")
    coefflist = []

    for coeff in coeffs:
        has_term = False
        for character in coeff:  # we look at the string representation
            if character in ascii_letters:
                has_term = True
                break
        if has_term:
            cut = 0
            for character in coeff:
                if character in digits \
                        or character == ".":
                    cut = cut + 1
                else:
                    if cut == 0:
                        coefflist.append(1)
                    else:
                        coefflist.append(float(term[0:cut]))
                    break

    return varlist, coefflist

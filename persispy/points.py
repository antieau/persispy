 # Summary of changes.
# hash_point.HashPoint moved to ../hash_point.py
# "points_*" in definition removed.

'''
File: examples.py

Several functions that produce instances of the PointCloud class.

AUTHORS:

    - Benjamin Antieau (2015-04)
    - Daniel Etrata (2016-09)

This module contains several functions that produce PointClouds, and it
contains the definition of the hashing.HashPoint class. This provides
a wrapping up a numpy.array that is suitable for hashing. A hashable
'point' is necessary for certain subroutines of the PointCloud class,
especially the neighborhood_graph function.
'''

import numpy as np
import numpy.random as npr


from persispy.hashing import HashPoint
try:
    from persispy.phc import Intersect
except ImportError:
    print("PHCpy is not currently installed. PHC functions are unavailable.")
from persispy.point_cloud import PointCloud

equations = {
    "circle": "x^2 + y^2 - 1",
    "sphere": "x^2 + y^2 + z^2 - 1",
    "torus": "16*x^2 + 16*y^2 - (x^2 + y^2 + z^2 + 3)^2",
    "eightsurface": "4*z^4 + 1/2 * (x^2 + y^2 - 4*z^2) - 1/4",
    "hyperbolid": "x^2 + y^2 - z^2 - 1",
    "degree3sphere": "x^3 + y^3 + z^3 - 1"
}


def intersect_hyperbolid(number_of_points):
    """
    Returns points on the hyperbolid.
    """
    return Intersect(equations["hyperbolid"], number_of_points)


def intersect_eightsurface(number_of_points):
    """
    Returns points on an eightsurface.
    """
    return Intersect(equations["eightsurface"], number_of_points)


def intersect_torus(number_of_points):
    """
    Returns points on a torus.
    """
    return Intersect(equations["torus"], number_of_points)


def intersect_circle(number_of_points):
    """
    Returns points on a circle.
    """
    return Intersect(equations["circle"], number_of_points)


def intersect_sphere(number_of_points):
    """
    Returns points on a sphere.
    """
    return Intersect(equations['sphere'], number_of_points)


def circle(num_points, radius=1):
    '''
    Returns a PointCloud with num_points random points on the circle
    (1-sphere) of given radius centered at the origin in R^2.

    >>> circle(1000,radius=4)
    Point cloud with 1000 points in real affine space of dimension 2
    '''
    angles = np.array([(2 * np.pi) * npr.random() for _ in range(num_points)])
    return PointCloud([HashPoint([np.cos(theta), np.sin(theta)], index)
                       for index, theta in enumerate(angles)])

# 3d examples


def sphere(num_points, radius=1, method='rejection'):
    '''
    Returns a PointCloud with num_points random points on the 2-sphere
    of given radius.
    With method=='normalized', random points are plotted in the unit
    cube, and then divided by their length.
    With method=='rectangular', random polar coordinates are given.
    With method=='rejection', a rejection method is given to produce
    actually equidistributed points on the 2-sphere with its usual
    measure.

    >>> sphere(1000,radius=4)
    Point cloud with 1000 points in real affine space of dimension 3
    '''
    def normalize(x):
        """
        Helper func to normalize set of points to the radius.
        """
        return (radius / np.sqrt(sum(x * x))) * x
    if method == 'normalized':
        return PointCloud([
            HashPoint(normalize(2 * npr.random(3) - 1),
                      index=n) for n in range(num_points)], space='affine')
    elif method == 'rectangular':
        angles = np.array([2 * np.pi * npr.random(2)
                           for n in range(num_points)])
        return PointCloud(
            [
                HashPoint(
                    radius *
                    np.array(
                        [
                            np.sin(
                                angles[n][0]) *
                            np.cos(
                                angles[n][1]),
                            np.sin(
                                angles[n][0]) *
                            np.sin(
                                angles[n][1]),
                            np.cos(
                                angles[n][0])]),
                    index=n) for n in range(num_points)],
            space='affine')
    elif method == 'rejection':
        count = 0
        points = []
        while count < num_points:
            pt = 2 * radius * npr.random(3) - radius
            if np.sqrt(sum(pt * pt)) <= radius:
                points.append(HashPoint(pt, count))
                count = count + 1
        return PointCloud(points, space='affine')
    else:
        raise TypeError('The argument "method" should be either' +
                        '"normalized", "rectangular", or "rejection".')


def torus(num_points, gui=False):
    '''
    >>> torus(1000)
    Point cloud with 1000 points in real affine space of dimension 3
    '''
    angles = np.array([2 * np.pi * npr.random(2) for n in range(num_points)])
    hp = [
        HashPoint(
            np.array(
                [(2 + np.cos(angles[n][0])) * np.cos(angles[n][1]),
                 (2 + np.cos(angles[n][0])) * np.sin(angles[n][1]),
                 np.sin(angles[n][0])]),
            index=n) for n in range(num_points)]
    return PointCloud(hp, space='affine', gui=gui)


def flat_torus(num_points):
    '''
    >>> flat_torus(1000)
    Point cloud with 1000 points in real affine space of dimension 4
    '''
    angles = np.array([2 * np.pi * npr.random(2) for n in range(num_points)])
    return PointCloud([
        HashPoint(
            np.array(
                [np.cos(angles[n][0]),
                 np.sin(angles[n][0]),
                 np.cos(angles[n][1]),
                 np.sin(angles[n][1])]),
            index=n) for n in range(num_points)], space='affine')


def cube(dim, num_points):
    '''
    >>> cube(4,1000)
    Point cloud with 1000 points in real affine space of dimension 4
    '''
    return PointCloud([HashPoint(npr.random(dim), index=n)
                       for n in range(num_points)], space='affine')


def box(number_of_points,
        dimension=2,
        side_length=1,
        seed=False,
        return_seed=False):
    """
    We return a set of points in a box of given dimension. On default,
    returns a unit box in the plane. We can specify a str or int seed.
    We can also ask to return the seed used to generate a run. Note, the
    returned seed is a ndarray of 624 units and is returned as a tuple.

    >>> box(1000, 2)
    Point cloud with 1000 points in real affine space of dimension 2

    >>> box(1000, dimension=4)
    Point cloud with 1000 points in real affine space of dimension 4

    """
    if seed:
        npr.seed(seed)

    result = PointCloud(
        [HashPoint(
            npr.uniform(-side_length / 2,
                        side_length / 2,
                        size=dimension),
            index=n)
         for n in range(number_of_points)],
        space='affine')

    if return_seed:
        return_seed = npr.get_state()
        result = (result, return_seed)

    return result

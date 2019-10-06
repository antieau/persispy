'''
File: point_cloud.py

The PointCloud data structure and related functions.

AUTHORS:

    - Benjamin Antieau (2015-04)
    - Mason Boeman (2015-04)
    - Daniel Etrata (2015-11)
'''

import math

import numpy as np
# from numpy import array
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import mpl_toolkits.mplot3d.axes3d as plt3
# import mpl_toolkits.mplot3d as a3

from persispy.weighted_simplicial_complex import wGraph
from persispy.hashing import HashPoint
from random import randint
# from persispy.hashing import HashEdge


class PointCloud(object):

    '''
    The :class:`PointCloud` class returns a point cloud with the
    properties of being hashable, which is necessary for indexing
    a dictionary.

    :param list points: A list of points
    :param str space: [affine|projective] The space the points live in.
    :param bool gui: Used by :mod:`persispy.plot` to either display or return the plot

    '''

    def __init__(self, points, space='affine', gui=False):
        if type(points) is not np.ndarray:
            points = np.array(points)
        try:
            self._points = list(points)
        except TypeError:
            raise TypeError('Input points should be a list of points.')
        try:
            hash(self._points[0])
        except TypeError:
#             print("Detected points are not hashable." +
#                   "Attempting to convert to HashPoints.")
            self._points = [HashPoint(points[n],
                                      index=n) for n in range(len(points))]
        if space != 'affine' and space != 'projective':
            raise TypeError('The argument "space" should be set to' +
                            'either "affine" or "projective".')

        self._space = space
        self._fig = None
        self.gui = gui

    def __repr__(self):
        try:
            repr(self.dimension())
        except AttributeError:
            raise AttributeError(
                'The numpy array must be a single set of points.')
        return 'Point cloud with ' + repr(self.num_points()) + \
            ' points in real ' + self._space + \
            ' space of dimension ' + repr(self.dimension())

    def get_points(self):
        """
        We return the PointCloud's points.
        """
        return self._points

    def get_space(self):
        """
        We return the PointCloud's space.
        """
        return self._space

    def __len__(self):
        return len(self._points)

    def size(self):
        """
        Returns the number of points in the point cloud.
        """
        return len(self._points)

    def __getitem__(self, key):
        return tuple(self._points[key].coordinate())

    def num_points(self):
        """
        Legacy function.
        Returns the number of points in the point cloud.
        """
        return self.size()

    def dimension(self):
        """
        Returns the dimension of the point cloud.
        """
        if self._space == 'affine':
            return len(self._points[0].coordinate())
        elif self._space == 'projective':
            return len(self._points[0].coordinate()) - 1

    def plot2d(self, *args, **kwargs):
        """
        redirecting plotting methods
        """
        from persispy.plot import plot2d
        print ("warning: PointCloud.plot2d() depreciated, use instead")
        print (">>> persispy.plot.plot2d(PointCloud)")
        plot2d(self, *args, **kwargs)

    def plot3d(self, *args, **kwargs):
        """
        redirecting plotting methods
        """
        from persispy.plot import plot3d
        print ("warning: PointCloud.plot3d() depreciated, use instead")
        print (">>> persispy.plot.plot3d(PointCloud)")
        plot3d(self, *args, **kwargs)

    def plot2d_neighborhood_graph(self, epsilon, *args, **kwargs):
        """
        redirecting plotting methods
        """
        from persispy.plot import plot2d
        print ("warning: PointCloud.plot2d_neighborhood_graph()" +
               "depreciated, use instead")
        print (">>> persispy.plot.plot2d(wGraph)")
        wgraph = self.neighborhood_graph(epsilon)
        plot2d(wgraph, *args, **kwargs)

    def plot3d_neighborhood_graph(self, epsilon, *args, **kwargs):
        """
        redirecting plotting methods
        """
        from persispy.plot import plot3d
        wgraph = self.neighborhood_graph(epsilon)
        print ("warning: PointCloud.plot3d_neighborhood_graph()" +
               "depreciated, use instead")
        print (">>> persispy.plot.plot3d(wGraph)")
        plot3d(wgraph, *args, **kwargs)

    def neighborhood_graph(self,
                           epsilon,
                           method="subdivision"):
        """
        calls its recursive function

        :param float epsilon: maximum distance between points
        :param str method: [exact|subdivision|subdivision 3|subdivision 7 approximate]
        :return: a :class:`wGraph` of the form ``{point: {adj_points:distance}}``
        .. automethod:: _neighborhood_graph
        """
        return self._neighborhood_graph(epsilon,
                                        method,
                                        self._points,
                                        {v: set() for v in self._points})

    def _neighborhood_graph(self,  # pylint: disable = R0911, R0912
                            # too many branches and too many return values
                            epsilon,
                            method,
                            pointarray,
                            dictionary):
        '''
        The 'method' string is separated by spaces. Acceptable values:

        "exact"
                does "exact"
        "subdivision"
                does "subdivision" to infinite depth
        "subdivision 3"
                does "subdivision" to depth 3, then "exact"
        "subdivision 7 approximate"
                does "subdivision" to depth 7, then "approximate"

        returns {point: {adj_points:distance}}

        '''
        methodarray = method.split(' ')

        if methodarray[0] == 'subdivision':

            if self._space == 'projective':
                return self.neighborhood_graph(epsilon, method='exact')
            elif self._space == 'affine':
                if len(methodarray) > 1:
                    d = int(methodarray[1])
                    m = ''
                    for i in range(len(methodarray) - 2):
                        m = m + methodarray[i + 2]
                        m = m + ' '

                    if m == '':
                        self._subdivide_neighbors(epsilon,
                                                  dictionary,
                                                  pointarray,
                                                  depth=d)
                        return wGraph(dictionary, epsilon)
                    else:
                        self._subdivide_neighbors(epsilon,
                                                  dictionary,
                                                  pointarray,
                                                  coordinate=m,
                                                  depth=d)
                        return wGraph(dictionary, epsilon)
                else:
                    self._subdivide_neighbors(epsilon, dictionary, pointarray)
                    return wGraph(dictionary, epsilon)

        elif methodarray[0] == 'exact':
            for i in range(len(self._points)):
                for j in range(i + 1, len(self._points)):
                    if self._space == 'affine':
                        dist = np.sqrt(
                            sum((self._points[i].coordinate() -
                                 self._points[j].coordinate())**2))
                        if dist < epsilon:
                            dictionary[self._points[i]].add(
                                (self._points[j], dist))
                            dictionary[self._points[j]].add(
                                (self._points[i], dist))
                    elif self._space == 'projective':
                        return None
            return wGraph(dictionary, epsilon)

        elif methodarray[0] == 'approximate':
            return None
        elif methodarray[0] == 'randomized':
            return None
        elif methodarray[0] == 'landmarking':
            return None

        else:
            raise TypeError(
                'Method should be one of subdivision, exact, approximate, ' +
                'randomized, or landmarking.')



    def _selectpoint(self, pointarray, k, n):
        """
        We return the kth smallest point of :data:pointarray, according to the
        nth coordinate. We use this to give the median, but a general
        solution for k is needed for the recursive algorithm. This
        algorithm is O(n) for best and worst cases.
        """

        a = pointarray[:]
        c = []

        if len(pointarray) == 1:
            return a[0]

        while(len(a) > 5):
            for x in range(int(math.floor(len(a) / 5))):
                b = pointarray[5 * x: 5 * x + 5]
                b.sort(key=lambda x: x.coordinate()[n])
                c.append(b[int(math.floor(len(b) / 2))])
            a = c
            c = []
        pivot = a[int(math.floor(len(a) / 2))]

        lesser = [
            point for point in pointarray
            if point.coordinate()[n] < pivot.coordinate()[n]]
        if len(lesser) > k:
            return self._selectpoint(lesser, k, n)  # recursive
        k -= len(lesser)

        equal = [
            point for point in pointarray
            if point.coordinate()[n] == pivot.coordinate()[n]]
        if len(equal) > k:
            return pivot  # basecase
        k -= len(equal)

        greater = [
            point for point in pointarray
            if point.coordinate()[n] > pivot.coordinate()[n]]
        return self._selectpoint(greater, k, n)  # recursive

    def _subdivide_neighbors(self,  # pylint: disable = R0914
                             epsilon,  # too many local variables
                             dictionary,
                             pointarray,
                             coordinate=0,
                             method='exact',
                             depth=-1):
        """
        method and depth are accumulators for the recursive calls
        divides the space into two regions about the median point
        relative to "coordinate" glues the two regions, then recursively
        calls itself on the two regions.
        """
        if len(pointarray) > 1:
            median = self._selectpoint(
                pointarray, math.floor(len(pointarray) / 2), coordinate)
            smaller = []
            bigger = []
            gluesmaller = []
            gluebigger = []

            for i, _ in enumerate(pointarray):  # split into two regions


                if randint(0,1):
                    if pointarray[i].coordinate()[coordinate] <= \
                            median.coordinate()[coordinate]:
                        smaller.append(pointarray[i])
                        if (pointarray[i].coordinate()[coordinate] >
                                median.coordinate()[coordinate] - epsilon):
                            gluesmaller.append(pointarray[i])

                    if pointarray[i].coordinate()[coordinate] > \
                            median.coordinate()[coordinate]:
                        bigger.append(pointarray[i])
                        if (pointarray[i].coordinate()[coordinate] < \
                                median.coordinate()[coordinate] + epsilon):
                            gluebigger.append(pointarray[i])

                else:
                    if pointarray[i].coordinate()[coordinate] < \
                            median.coordinate()[coordinate]:
                        smaller.append(pointarray[i])
                        if (pointarray[i].coordinate()[coordinate] >
                                median.coordinate()[coordinate] - epsilon):
                            gluesmaller.append(pointarray[i])

                    if pointarray[i].coordinate()[coordinate] >= \
                            median.coordinate()[coordinate]:
                        bigger.append(pointarray[i])
                        if (pointarray[i].coordinate()[coordinate] < \
                                median.coordinate()[coordinate] + epsilon):
                            gluebigger.append(pointarray[i])

            for i, _ in enumerate(gluesmaller):  # glue together two regions
                for j, _ in enumerate(gluebigger):
                    dist = np.sqrt(
                        sum(((gluesmaller[i]).coordinate() -
                             gluebigger[j].coordinate()) *
                            (gluesmaller[i].coordinate() -
                             gluebigger[j].coordinate())))
                    if dist < epsilon:
                        dictionary[gluesmaller[i]].add((gluebigger[j], dist))
                        dictionary[gluebigger[j]].add((gluesmaller[i], dist))

            coordinate = (coordinate + 1) % self.dimension()
            if depth == -1:  # full recursive. all edges are formed by "gluing"
                self._subdivide_neighbors(
                    epsilon, dictionary, smaller, coordinate, method, depth=-1)
                self._subdivide_neighbors(
                    epsilon, dictionary, bigger, coordinate, method, depth=-1)
            elif depth == 0:
                self._neighborhood_graph(epsilon, method, smaller, dictionary)
                self._neighborhood_graph(epsilon, method, bigger, dictionary)
            elif depth > 0:
                self._subdivide_neighbors(
                    epsilon, dictionary, smaller, coordinate, method, depth-1)
                self._subdivide_neighbors(
                    epsilon, dictionary, bigger, coordinate, method, depth-1)




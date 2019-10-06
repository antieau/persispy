'''
File: hashing.py

Hashable data points wrapping numpy arrays.

AUTHORS:

    - Benjamin Antieau (2015-04)
    - Daniel Etrata (2016-01)
'''

import hashlib as hashlib
import numpy as np


class HashPoint(object):
    '''
    A wrapped numpy array to allow hashing.

    Vars: _coords (a numpy array).

    >>> HashPoint([1,2,3])
    point 0: [1, 2, 3]
    '''

    def __init__(self, coords, index=0):
        self._coords = np.array(coords)
        self._index = index

    def __len__(self):
        return len(self._coords)

    def __getitem__(self, key):
        return self._coords[key]

    def __hash__(self):
        try:
            out = self._hash
            return out
        except AttributeError:
            self._hash = int(hashlib.sha1(self._coords.view()).hexdigest(), 16)
            return self._hash

    def __repr__(self):
        return "point " + str(self._index) + ": " + \
            str(self._coords.__repr__())[6:-1]

    def point(self):
        '''
        .items()

        >>> x = HashPoint([1,2,3])
        >>> x.point()
        (0, array([1, 2, 3]))
        '''
        return self._index, self._coords

    def index(self):
        """
        .keys()

        >>> x = HashPoint([1,2,3], 99)
        >>> x.index()
        99
        """
        return self._index

    def coordinate(self):
        '''
        .values()

        >>> x = HashPoint([1,2,3])
        >>> x.coordinate()
        array([1, 2, 3])
        '''
        return self._coords

    # The <,>,<=,>= comparators below use only the index to compare points. The
    # == and != comparators behave as follows. Two hash points will return x==y
    # as True if and only if they have the same index and the same _coords.
    # Otherwise, they are not equal (i.e., __ne__ returns True), even if they
    # have the same index. This has
    # a possibly strange consequence. One can have x<y False, x<=y True, but
    # x!=y also True.
    def __lt__(self, other):
        return self._index < other.index()

    def __gt__(self, other):
        return other < self

    def __le__(self, other):
        return self._index <= other.index()

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        coordinate_cmp = True
        # Note that for numpy.arrays x=numpy.array([1,2,3]) and
        # y=numpy.array([1,4,5]), x==y will return another numpy array, namely
        # array([ True,  False,  False], dtype=bool).
        for _coordinate in self._coords == other.coordinate():
            if _coordinate:
                continue
            else:
                coordinate_cmp = False
                break
        return self._index == other.index() and coordinate_cmp

    def __ne__(self, other):
        return not self == other

#    # Depreciated in python3.
#    def __cmp__(self, other):
#        return self._index.__cmp__(other._index)


class HashEdge(object):
    '''
    This acts like a dict.

    A wrapped numpy array to allow hashing.

    Takes a single pair of points which defines an edge.
    Points can either be a np.array, a tuple or a list.

    >>> HashEdge(np.array(([0,0,0],[1,1,1])), index = 99)
    edge 99: [[0 0 0] [1 1 1]]
    '''

    def __init__(self, edge, index=0, DEBUG=False):

        self._index = index
        if DEBUG:
            print(edge)

# assumes an undirected graph, where point and endPoints are unordered
# allows cmp to compare the edge
# "(0, 1)" assumes an a vertex and an endPoint

        for point in (0, 1):
            edge = sorted(edge,
                          key=lambda component, p=point: component[p])

        if isinstance(edge, np.float64):
            self._edge = edge
        else:
            self._edge = np.array(edge)

    def __len__(self):
        return len(self.edge)

    def __getitem__(self, key):
        return self._edge[key]

    def __hash__(self):
        try:
            out = self._hash
            return out
        except AttributeError:
            self._hash = int(hashlib.sha1(self._edge.view()).hexdigest(), 16)
            return self._hash

    def __repr__(self):
        '''

        >>> e = HashEdge(np.array(([1,2,3],[1,1,1])), index = 99)
        >>> print(e)
        edge 99: [[1 1 1] [1 2 3]]

        '''
        return ("edge " +
                str(self._index) +
                ": %s" % str(self._edge).replace('\n', ''))

    def edge(self):
        '''

        >>> e = HashEdge(np.array(([0,0,0],[1,1,1])), index = 99)
        >>> e.edge()
        (99, array([[0, 0, 0],
               [1, 1, 1]]))

        '''
        return self._index, self._edge

    def index(self):
        '''

        >>> e = HashEdge(np.array(([0,0,0],[1,1,1])), index = 99)
        >>> e.index()
        99
        '''
        return self._index

    def vertices(self):
        '''

        >>> e = HashEdge(np.array(([0,0,0],[1,1,1])), index = 99)
        >>> e.vertices()
        array([[0, 0, 0],
               [1, 1, 1]])


        '''
        return self._edge

    def __cmp__(self, other):
        """
        >>> HashEdge(np.array(([0,0,0],[1,2,3]))) == \
                HashEdge(np.array(([0,0,0],[1,2,3])))
        True
        >>> HashEdge(np.array(([0,0,0],[1,1,1]))) == \
                HashEdge(np.array(([1,1,1],[0,0,0])))
        True
        >>> HashEdge(np.array(([0,0,0],[1,1,1]))) == \
                HashEdge(np.array(([0,0,0],[2,2,2])))
        False
        """
        return (self._edge.flatten() == other._edge.flatten()).all()

    def __eq__(self, other):
        return self.__cmp__(other)

    def __mul__(self, other):
        """
        >>> HashEdge([[0,0,0],[1,1,3]]) * 2
        edge 0: [[0 0 0] [2 2 6]]
        """
        if not isinstance(other, float) \
                and not isinstance(other, int):
            raise NotImplementedError("Cannot multiply type %s" % type(other))
        newedge = []
        for point in self._edge:
            newedge.append([component * other for component in point])

        return HashEdge(np.array(newedge), self._index)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

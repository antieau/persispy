"""

AUTHORS:

    - Benjamin Antieau (2015-04)
    - Mason Boeman (2015-04)
    - Daniel Etrata (2015-11)
We create a undirected weighted graph from a point cloud.
"""
import itertools
import sys
import numpy.random as npr
from numpy import array
from itertools import combinations
from persispy.hashing import HashEdge
from pprint import PrettyPrinter

DEBUG = False


class wSimplex(object):
    '''
    An oriented simplex.
    '''

    def __init__(self, vertices, weight):
        '''
        The orientation is the one given by the list of vertices.

        Variables:
            _vertices: a list of points.
            _weight: the weight. The maximum edge of a simplex.

        >>> from persispy.hashing import HashPoint
        >>> wSimplex(vertices = [HashPoint(coords = (0,0,0), index = 0), \
                            HashPoint((1,0,0), index = 1)], \
                    weight = 1)
        Weighted simplex (point 0: [0, 0, 0], point 1: [1, 0, 0]) with weight 1
        '''

        self._vertices = tuple(sorted(list(vertices), key=lambda v: v.index()))
        self._size = len(vertices)
        self._weight = weight
        self._index = -1  # the compatible total ordering

    def weight(self):
        """
        Returns the weight of the simplex.
        """
        return self._weight

    def vertices(self):
        """
        Returns the set of vertices in a simplex as a tuple.
        """
        return self._vertices

    def __repr__(self):
        return 'Weighted simplex ' + str(
            self._vertices) + ' with weight ' + str(self._weight)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __eq__(self, other):
        return self.compare(other) == 0

    def __ne__(self, other):
        return not self == other

    def compare(self, other):
        """
        Legacy comparison method for hashing.
        """
        value = 0.0
        finished = False
        if (self._weight != other.weight()) and not finished:
            value = self._weight - other.weight()
            finished = True
        if (len(self._vertices) != len(other.vertices())) and not finished:
            value = len(self._vertices) - len(other.vertices())
            finished = True
        if not finished:
            if self._vertices != other.vertices():
                for i in range(len(self._vertices)):
                    if self._vertices[i] != other.vertices()[i]:
                        if self._vertices[i] < other.vertices()[i]:
                            return -1
                        if self._vertices[i] > other.vertices()[i]:
                            return 1
        if value < 0:
            return -1
        if value > 0:
            return 1
        return 0


class wGraph(object):
    '''
    :param dict adjacencies: The adjacency dictionary is the set of edges indexed by vertices.
    :param float epsilon: The maximum distance between neighbors
    :return: a :class:`wGraph`

    '''

    def __init__(self, adjacencies, epsilon):
        if epsilon is None:
            raise NotImplementedError()
        self._adj = adjacencies
        self._epsilon = epsilon
        self._connected_components = None
        self._edges = None

        # place holder for more efficient recursive coding
        # .connnected_components() has issues without the following line
        if len(adjacencies) > 1000:
            sys.setrecursionlimit(len(adjacencies))

    @classmethod
    def from_edge_list(cls, vertices, edges, validate=False):
        '''
        NOTE: vertices needs to be a set or list of hashable objects.
        '''
        if validate:
            for e in edges:
                if len(e) != 3:
                    raise TypeError('Edges are lists of pairs of distinct' +
                                    'vertices followed by a weight.')
                if e[0] == e[1]:
                    raise TypeError('Edges are lists of pairs of distinct' +
                                    'vertices followed by a weight.')

        adj = {v: set() for v in vertices}
        for e in edges:
            adj[e[0]].add((e[1], e[2]))
            adj[e[1]].add((e[0], e[2]))
        return cls(adj, None)

    def __repr__(self):
        """
        We define 'print(wGraph)'.
        """
        return('Weighted graph with ' + repr(self.num_points()) +
               ' points and ' + repr(self.num_edges()) + ' edges')

    def __len__(self):
        """
        We define 'len(wGraph)' to be the number of edges.
        Also see .order() and .num_edges()
        """
        return self.num_edges()

    def epsilon(self):
        """
        We return the epsilon of the wGraph.
        """
        return self._epsilon

    def adjacencies(self, pretty=False):
        """
        We return the adjacency dictionary.
        """
        if pretty:
            pp = PrettyPrinter()
            return pp.pformat(self._adj)
        elif not pretty:
            return self._adj


    def get_points(self):
        """
        We return the points of the wGraph.
        """
        return self.vertices()

    def vertices(self):
        """
        We return the points of the wGraph.
        """
        return self._adj.keys()

    def num_points(self):
        """
        We return the number of points in the wGraph.
        """
        return len(self._adj.keys())

    def order(self):
        """
        We return the number of edges of the wGraph.
        """
        return self.num_edges()

    def num_edges(self):
        """
        We return the number of edges of the wGraph.
        """
        count = 0
        for v in self._adj.keys():
            count = count + len(self._adj[v])
        return int(count / 2)

    def degree(self, p):
        """
        returns the degree of the point
        """
        return len(self._adj[p])

    def metric(self, p, q):
        """
        Returns the distance between two points.
        """
        if p not in self._adj.keys() or q not in self._adj.keys():
            raise ValueError('The points must be vertices.')
        else:
            for e in self._adj[p]:
                if e[0] == q:
                    return e[1]
            return -1

    def connected_component(self, point, visited, time):
        """
        RECURSIVE
        We note the time passed by the input when a node was visited in the
        'visited' dict. We then call itself on any adjacent nodes that have
        not been visted.
        """
        if DEBUG:
            print(time)
        visited[point] = time
        for neighbor in self._adj[point]:
            if not visited[neighbor[0]]:  # uses the fact that 0 evals to False
                self.connected_component(neighbor[0], visited, time)

    def connected_components(self):
        '''
        We returns a list giving the connected components of the wGraph.
        NOTICE: Gives only a depth first search tree. This is to save operations
        if our only goal is to count the number of connected components.
        Call .connected_edges() for the connected component with edges.
        '''
        visited = {d: 0 for d in self._adj}

        time = 0
        for point in self._adj:  # runs in O(|points| + |edges|)
            if visited[point] == 0:
                time = time + 1
                self.connected_component(point, visited, time)

        components = []
        for connected in range(1, time + 1):  # runs in O(|components|)
            component = []
            for point in visited:  # runs in O(|points in component|)
                if visited[point] == connected:
                    component.append(point)
            if component:
                components.append(component)

        self._connected_components = components

        return components

    def singletons(self, padding=False):
        """
        We return the singletons.
        """
        if not self._connected_components:
            self.connected_components()
        cp = self._connected_components
        if DEBUG:
            for item in cp:
                print(item)

        singles = []
        for component in cp:
            if len(component) == 1:  # if the component is a point
                component = list(component[0])
                if DEBUG:
                    print(component)
                while len(component) < padding:
                    component.append(0)
                if DEBUG:
                    print(component)
                singles.append(component)
        return singles

    def connected_edges(self, padding=False):
        """
        Returns a list of edges that make up a connected component. We assume
        no multiple edges.
        NOTE: We do not include single points. See .singletons()
        """

        if not self._connected_components:
            self.connected_components()
        cp = self._connected_components

        components = []
        for component in cp:
            edges = {}
            if len(component) > 1:  # if the component is not a point
                edgeIndex = 0
                for vertex in component:
                    vertexList = list(vertex)
                    while len(vertexList) < padding:
                        vertexList.append(0)
                    for endPoint in self._adj[vertex]:
                        endPointList = list(list(endPoint)[0])
                        while len(endPointList) < padding:
                            endPointList.append(0)
                        edges[edgeIndex] = HashEdge(
                            array([vertexList, endPointList]),
                            index=edgeIndex
                        )
                        edgeIndex += 1
            if edges:
                edges = edges.values()
                edges = set(edges)
                components.append(edges)

        self._edges = components
        return components

    def cloud_dist(self, pointlist):
        '''
        Returns the maximum of the distances of all pairs of points in
        pointlist.
        '''
        dist = 0
        if len(pointlist) == 1:
            return dist
        for t in combinations(pointlist, 2):
            d = self.metric(t[0], t[1])
            if d >= 0:
                dist = max(dist, d)
            else:
                return -1
        return dist

    def neighborhood_graph(self, epsilon):
        '''
        INPUT: epsilon.
        OUTPUT: the subgraph consisting of those edges with weight less
        than epsilon.
        '''
        keys = self._adj.index()
        adj = {v: [] for v in keys}
        for k in keys:
            for v in self._adj[k]:
                if v[1] < epsilon:
                    adj[k].append(v)
        return wGraph(adj, None)


def wRandomGraph(n, p, epsilon):
    '''
    Returns the Gilbert (Erdos-Renyi) random graph G(n,p), which
    includes each edge independently with probability 0<p<1. A random
    weight in the range [0,epsilon) is assigned to each edge.
    '''
    dictionary = {v: [] for v in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if npr.random() < p:
                w = epsilon * npr.random()
                dictionary[i].append([j, w])
                dictionary[j].append([i, w])
    return wGraph(dictionary, epsilon)


class wSimplicialComplex(object):
    """
    From a wgraph and it's simplicies, we setup the weighted simplicial
    complex.
    """

    def __init__(self, wgraph, simplices):
        self._wgraph = wgraph
        self._simplices = simplices

    @classmethod
    def from_clique_list(cls, wgraph, cliques, verify=False):
        '''
        Input: a wGraph together with a list of simplices on the vertex
        set of the graph. It is assumed (and not checked unless
        verify==True) that the 1-skeleton of every simplex is contained
        in the graph.
        '''

        full_simplex = {0: [wSimplex([k], 0)
                         for k in wgraph.adjacencies().keys()]}
        full_simplex[1] = []

        for t in combinations(wgraph.adjacencies().keys(), 2):
            if wgraph.metric(t[0], t[1]) > 0:
                full_simplex[1].append(wSimplex(t, wgraph.metric(t[0], t[1])))

        for v in cliques:
            if verify:  # 1-skeleton of v is included in wGraph
                for vlist in combinations(v, 2):
                    if wgraph.metric(vlist[0], vlist[1]) == -1:
                        raise ValueError('All cliques must have 1-skeleton' +
                                         'included in wgraph.')
            for d in range(3, len(v) + 1):
                for vlist in combinations(v, d):
                    # The next crudge is to make this bit backwards compatible
                    # with python2. Note that has_key() is no longer an
                    # attribute of dictionaries in python3.
                    # TEST: I have not tested it on python2 as of 19 March 2016.
                    try:  # Python2
                        if not full_simplex.has_key(d-1):
                            full_simplex[d - 1] = []
                    except AttributeError:
                        if not d - 1 in full_simplex:
                            full_simplex[d - 1] = []
                    weight = 0
                    for i in range(d - 1):
                        inbrs = wgraph.adjacencies()[vlist[i]]
                        for j in inbrs:
                            if j[0] in vlist:
                                weight = max(weight, j[1])
                    new_simplex = wSimplex(vlist, weight)
                    if new_simplex not in full_simplex[d - 1]:
                        full_simplex[d - 1].append(new_simplex)
        return wSimplicialComplex(wgraph, full_simplex)

    def __repr__(self):
        return(repr(self.dimension()) + '-dimensional weighted' +
               'simplicial complex with ' + repr(len(self._simplices[0])) +
               ' vertices and ' + repr(self.simplices_positive()) +
               ' positive-dimensional simplices')

    def simplices_positive(self):
        """
        ?
        """
        return sum([len(self._simplices[k])
                    for k in range(1, self.dimension() + 1)])

    def simplices(self, pretty=False):
        """
        Return the simplices.
        """
        if pretty:
            pp = PrettyPrinter()
            return pp.pformat(self._simplices)
        elif not pretty:
            return self._simplices
        return self._simplices

    def dimension(self):
        """
        Returns the dimension of the complex.
        """
        dim = 0
        for k in self._simplices.keys():
            if len(self._simplices[k]) > 0:
                dim = max(k, dim)
        return dim

    def simplex_sort(self):
        '''
        Sorts the simplices with respect to the lexographic ordering
        dictated by the ordering of the vertices implicit in the list
        self._simplices[0].
        '''
        dictionary = [x.vertices()[0] for x in self._simplices[0]]

        def simplex_cmp_lex(s, t):
            """
            Helper function.
            """
            sindices = tuple([dictionary.index(x) for x in s.vertices()])
            tindices = tuple([dictionary.index(x) for x in t.vertices()])
            return cmp(sindices, tindices)
        for d in range(1, self.dimension() + 1):
            self._simplices[d].sort(simplex_cmp_lex)

        return None

#     def VRComplex(self, epsilon):
#         vertices = self._wgraph.adjacencies().index()
#         edges = dict()
#         for v in vertices:
#             new_edges = []
#             for e in self._wgraph.adjacencies()[v]:
#                 if e[1] < epsilon:
#                     new_edges.append(e)
#             edges[v] = new_edges
#         wg = wgraph.wGraph(edges)
#         simplices = dict()
#         for d in self._simplices.index():
#             simplices[d] = []
#             for s in self._simplices[d]:
#                 if s.weight() < epsilon:
#                     simplices[d].append(s)
#         return wSimplicialComplex(wg, simplices)


class sorted_clique_list(object):

    def __init__(self, wg):
        '''wg is a weighted graph'''
        self._cliques = []
        sorted_clique_list._BronKerboschPivot(
            set(),
            set(wg.adjacencies().keys()),
            set(),
            wg.adjacencies(),
            self._cliques)
        self._cliques.sort()

    def get_simplex_iterator(self, n):
        '''
        gives an iterable which includes all n simplices
        '''
        i = set()
        for x in self._cliques:
            if len(x) >= n + 1:
                i.update(itertools.combinations(x, n + 1))
        return _clique_iterator(iter(i))

    def get_ordered_simplex_iterator(self, n):
        i = set()
        for x in self._cliques:
            if len(x) >= n + 1:
                i.update(itertools.combinations(x, n + 1))
        return _clique_iterator(iter(sorted(list(i))))

    def get_full_simplex_iterator(self, n):
        '''
        gives an iterable which includes all k simplices for k <= n
        '''
        i = self.get_simplex_iterator(n)
        j = []
        for c in self._cliques:
            if len(c) < n + 1:
                j.append(c)
        return _clique_iterator(itertools.chain(iter(j), i))

    @staticmethod
    def _BronKerbosch(r, p, x, adj, c):
        if (len(p) == 0 and len(x) == 0):
            c.append(sorted(tuple(r)))
        else:
            for v in set(p):
                nbh = {x[0] for x in adj[v]}
                sorted_clique_list._BronKerbosch(
                    r | {v}, p & nbh, x & nbh, adj, c)
                p.remove(v)
                x.add(v)

    @staticmethod
    def _BronKerboschPivot(r, p, x, adj, c):
        if (len(p) == 0 and len(x) == 0):
            c.append(sorted(tuple(r)))
        else:
            for u in p | x:
                break
            # u = iter(p | x).next()
            for v in iter(set(p) - adj[u]):
                nbh = {x[0] for x in adj[v]}
                sorted_clique_list._BronKerboschPivot(
                    r | {v}, p & nbh, x & nbh, adj, c)
                p.remove(v)
                x.add(v)


class _clique_iterator(object):

    def __init__(self, i):
        self.iterator = i

    def __iter__(self):
        return self

    def next(self):
        return tuple(self.iterator.next())

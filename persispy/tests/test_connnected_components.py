# TODO: epsilon is a function of coefficients, number of points, and degree

# import sys
# sys.setrecursionlimit(1000)

pDict = {
    "circle"           : "x^2 + y^2 - 1",
    "sphere"           : "x^2 + y^2 + z^2 - 1",
    "torus"            : "16*x^2 + 16*y^2 - (x^2 + y^2 + z^2 + 3)^2",
    "eightsurface"     : "4*z^4 + 1 * (x^2 + y^2 - 4*z^2)",
    "wideeightsurface" : "4*z^4 + 1/2 * (x^2 + y^2 - 4*z^2) - 1/4",
    "hyperbolid"       : "x^2 + y^2 - z^2 - 1",
    "degree3sphere"    : "x^3 + y^3 + z^3 - 1"
}


from persispy.samples import points
from sympy import symbols
from sympy.parsing.sympy_parser import parse_expr
from numpy.random import uniform
import os
from datetime import datetime
from numpy.random import random_integers
from random import choice

def make_csv(columnNames):
    today = datetime.today()
    filepath = "points-"+str(today.month)+"-"+str(today.day)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    testpath = filepath+'/data.csv'
    if not os.path.isfile(testpath):
        csv = open(testpath, 'w')
        csv.write(columnNames+"\n")
    else:
        csv = open(testpath, 'a')
    return csv

def points_setup():

    try: # runs if shapely if installed
        from persispy.tests.area import shapely_area
        csv = make_csv("Number of points, Distance, Connected components, Area")
    except:
        csv = make_csv("Number of points, Distance, Connected components")


    
    distance = 0.020
    while(distance < .3):
        print "running test", distance
        try:
            distance = distance + .005
            for num_points in range(10, 2000, 10):
                points_epsilon_tests(num_points, distance, csv)
#                     connected_components = points_epsilon_tests(num_points, distance, csv, eqn)
        except StandardError as inst:
            print inst
            print "skip"
            pass

    print "all tests have run"
    csv.close()


from persispy.phc.points import phc
from persispy.point_cloud import PointCloud
from persispy.weighted_simplicial_complex import wSimplex, wGraph, wSimplicialComplex

def points_epsilon_tests(num_points, distance, csv, eqn = False):

    row = []
    failures = []
    try:
        if eqn:
            pc = phc(eqn, num_points = num_points, return_complex = True)
            
        else:
            pc = points.plane(num_points)

        row.append(str(num_points))
        row.append(str(distance))
    except StandardError as inst:
        print inst
        failures.append(inst.args[0])
        return failures

    try:
        ng = pc.neighborhood_graph(distance, method = "subdivision")
        cp = len(ng.connected_components())
        print "connected componenets", cp
        row.append(str(cp))
    except StandardError as inst:
        print inst
        failures.append(inst.args[0])
        return failures
    
    try: # runs if shapely is installed
        diskArea = shapely_area(pc, distance)
        print "area:", diskArea
        row.append(str(diskArea))
    except:
        pass

    print ','.join(row)
    row[-1] = row[-1]+"\n"
    csv.write(','.join(row))
    return cp


def main():

    points_setup()


if __name__ == "__main__": main()
    
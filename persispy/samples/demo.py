from persispy import point_cloud
from persispy.samples import points
from persispy.phc.points import phc
def test_plots():
#     point_cloud.PointCloud.plot2d(points.sphere(1000))
    phc("x+y-1",500,DEBUG=True).plot3d()
#     point_cloud.PointCloud.plot3d(points.flat_torus(1000))
#     point_cloud.PointCloud.plot3d(points.cube(4,1000))
#     point_cloud.PointCloud.plot3d(points.torus(1000))

def test_weighted_graph():
    pc = points.torus(1000)
    ng = pc.neighborhood_graph(.1, method = "subdivision")
    print ng

    print len(ng.connected_components())

def main():
    test_plots()
#    test_weighted_graph()

if __name__=="__main__": main()

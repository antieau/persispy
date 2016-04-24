"""
input: pointCloud OR
    wGraph
"""

import numpy as np
# import time

import matplotlib
import matplotlib as mpl
from matplotlib.collections import LineCollection
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg \
    import FigureCanvasTkAgg, NavigationToolbar2TkAgg
try: # python3
    import tkinter as tk
except: # python2
    import Tkinter as tk
import mpl_toolkits.mplot3d as a3
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D
from persispy.point_cloud import PointCloud
from persispy.weighted_simplicial_complex import wGraph
try:
    from persispy.phc import Intersect
except:
    Intersect = type("None", (object,), {"None": None})
    print("PHCpy is not currently installed. PHC functions are unavailable.")


def create_fig():
    """
    We make calls to the backend so we can handle displaying the figures
    themselves.
    """
    def destroy():
        """
        We take care of all the closing methods.
        """
        root.destroy()
        root.quit()
        plt.close('all')

    def onsize(event):
        """
        Any resizing is handled properly.
        """
        root.winfo_width(), root.winfo_height()
# only time to call pyplot
    fig = plt.figure()
#     fig.set_size_inches(8, 8)
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", destroy)
    root.bind("<Configure>", onsize)
    frame = tk.Frame(root)
    frame.pack(side='top', fill='both', expand=1)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
#     canvas.get_tk_widget().pack()
    canvas._tkcanvas.pack(side='top', fill='both', expand=1)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    toolbar.pack()
    return fig, root


def get_canvas(root):
    """
    Function to find all children of a canvas object.
    """
    children = root.winfo_children()  # this returns a list
    for child in children:
        if child.winfo_children():
            # We add all of the child's children to the list as well.
            children.extend(child.winfo_children())

    for child in children:
        if isinstance(child, NavigationToolbar2TkAgg):
            return child

    assert False, "No Canvas in root"


def show(root):
    """
    We set up our own methods to display the Figure.
    """
    canvas = get_canvas(root)
#     canvas.update()
#     canvas.flush_events()
    canvas.draw()
    root.mainloop()


def plot2d(*args, **kwargs):
    """
    We call different methods depending on what instance is being passed.
    """
    for item in args:
        if isinstance(item, PointCloud) or isinstance(item, Intersect):
            fig = plot2d_pc(*args, **kwargs)
            return fig
        if isinstance(item, wGraph):
            return plot2d_ng(*args, **kwargs)


def plot3d(*args, **kwargs):
    """
    We call different methods depending on what instance is being passed.
    """
    for item in args:
        if isinstance(item, PointCloud) or isinstance(item, Intersect):
            return plot3d_pc(*args, **kwargs)
        if isinstance(item, wGraph):
            return plot3d_ng(*args, **kwargs)


def plot2d_pc(pointCloud, gui=False):
    """
    We plot a plot cloud.
    """

    points = pointCloud.get_points()
    xcoords = [p[0] for p in points]
    ycoords = [p[1] for p in points]

    fig, ax = plt.subplots(1)
    ax.scatter(xcoords, ycoords, marker='o', color="#ff6666")

    ax.grid(True)
    ax.axis(
        [1.1 * min(xcoords),
         1.1 * max(xcoords),
         1.1 * min(ycoords),
         1.1 * max(ycoords)])
    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

#     ax.set_xlim(-3,3)
#     ax.set_ylim(-3,3)
# what do?
#     plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)

    if gui:
        return fig
    else:
        plt.show(fig)



cmaps = ['Accent', 'Dark2', 'Paired', 'Pastel1',
         'Pastel1', 'Set1', 'Set2', 'Set3',
         'gist_earth', 'terrain', 'ocean',
         'gist_stern', 'brg', 'CMRmap', 'cubehelix',
         'gnuplot', 'gnuplot2', 'gist_ncar',
         'nipy_spectral', 'jet', 'rainbow',
         'gist_rainbow', 'hsv', 'flag', 'prism']

def get_cmap(cmap):
    if type(cmap) is int:
        print(cmaps[cmap])
        return plt.get_cmap(cmaps[cmap])
    if type(cmap) is str:
        return plt.get_cmap(cmap)
    assert False


def plot2d_ng(wGraph,
              shading_style='axes',
              axes=(0, 1),
              shading_axis=1,
              method='subdivision',
              title="2D Neighborhood Graph",
              gui=False,
              cmap='Paired'):
    """
    We plot the 2d neighborhood graph, taking the axes to shade on.
    """
    if shading_style == 'axes':
        color_by_ax(wGraph, axes, shading_axis, method,
                    title, gui)
    elif shading_style == 'component':
        color_by_component(wGraph, axes, cmap, method,
                           title, gui)


def pick_ax(coords, axes):
    """
    Small helper fuction to pick our the axes of interest.
    """
    point = []
    for ax in axes:
        point.append(coords[ax])
    return tuple(point)

def color_by_ax(wGraph, axes, shading_axis, method, title, gui):
    """
    We color the graph by applying a gradient to an axis.
    """
    points = wGraph.get_points()


    # For the two plotting directions
    minx = min(p[0] for p in points)
    maxx = max(p[0] for p in points)
    miny = min(p[1] for p in points)
    maxy = max(p[1] for p in points)

    # For the shading direction

    minz = min(p[shading_axis] for p in points)
    maxz = max(p[shading_axis] for p in points)


    adjacency = wGraph.get_adjacency()
    edges = []
    colors = []
    x, y, pointcolors = [], [], []
    for p in adjacency:
        if p[shading_axis] <= minz + (maxz - minz) / 2:
            px, py = pick_ax(p, axes)
            for e in adjacency[p]:
                qx, qy = pick_ax(e[0], axes)
                edges.append([
                    [qx, qy],
                    [px, py]])

                colors.append(((p[shading_axis] - minz) / (maxz - minz),
                               .5, .5, .5))
            x.append(px)
            y.append(py)
            pointcolors.append(
                ((p[shading_axis] - minz) / (maxz - minz), .5, .5, .5))

        elif p[shading_axis] >= minz + (maxz - minz) / 2:
            px, py = pick_ax(p, axes)
            for e in adjacency[p]:
                qx, qy = pick_ax(e[0], axes)
                edges.append([
                    [qx, qy],
                    [px, py]])

                colors.append(((p[shading_axis] - minz) / (maxz - minz),
                               .5, .5, .5))

            x.append(px)
            y.append(py)
            pointcolors.append(
                ((p[shading_axis] - minz) / (maxz - minz), .5, .5, .5))

    lines = mpl.collections.LineCollection(edges, color=colors)

    fig, ax = plt.subplots(1)

#     fig = Figure()
#     ax = fig.add_subplot(111)
    ax.add_collection(lines)
    fig.set_size_inches(10.0, 10.0)
    if title:
        fig.suptitle(title)
    ax.grid(True)
    ax.axis(
        [minx - .1 * abs(maxx - minx),
         maxx + .1 * abs(maxx - minx),
         miny - .1 * abs(maxy - miny),
         maxy + .1 * abs(maxy - miny)])

    ax.set_aspect('equal')

#     x, y = pick_ax(zip(*wGraph.vertices()))
    ax.scatter(x, y, marker='o', color=pointcolors, zorder=len(x))

    if gui:
        return fig
    else:
        plt.show(fig)


def pick_ax_edge(component, axes):
    selected_axes = []
    for edge in component:
        endpoint1 = []
        endpoint2 = []
        for ax in axes:
            endpoint1.append(edge[0][ax])
            endpoint2.append(edge[1][ax])
        selected_axes.append((endpoint1, endpoint2))
    return selected_axes

def color_by_component(wGraph, axes, cmap, method, title, gui):

    plt.rc('text', usetex=True)
    plt.rc('font', family='sans-serif: Computer Modern Sans serif')
    plt.axis('off')

#     fig = plt.figure()
    fig, window = create_fig()
    window.wm_title(title)
    ax = fig.add_subplot(1, 1, 1)
    epsilon = wGraph.get_epsilon()
    adj = wGraph.get_adjacency()
    cp = wGraph.connected_components()
    cmap = get_cmap(cmap)  # color mappings
    line_colors = cmap(np.linspace(0, 1, len(cp)))
    line_colors = line_colors[::-1]


    # [0, 0.1, 0.2 ... 1 ]

    ce = wGraph.connected_edges()
    ce.sort(key=len)

    componentIndex = -1
    for componentIndex, component in enumerate(ce):

        #         scalar = float(len(component)) / numberEdges + 1
        #         tempcomponent = []
        #         for i, edge in enumerate(component):
        #             tempcomponent.append(edge*scalar)
        #         component = set(tempcomponent)

        component = pick_ax_edge(component, axes)
        lines = mpl.collections.LineCollection(component)

#         if componentIndex % 2 == 1:
#
#             componentIndex = -1 * componentIndex
        lines.set_edgecolor(line_colors[componentIndex])
        ax.add_collection(lines)

    componentIndex += 1

    if wGraph.singletons():
        x, y = zip(*[pick_ax(point, axes) for point in wGraph.singletons()])
        ax.scatter(x, y,
                   marker='.',
                   s=15,
                   color=line_colors[componentIndex:],
                   label=r"\makebox[90pt]{%d\hfill}Singletons" % len(x))

    textstr = r'\noindent\makebox[90pt]{%d\hfill}Number of Points\\ \\'\
        r'\makebox[90pt]{%.3f\hfill}Distance\\ \\'\
        r'\makebox[90pt]{%d\hfill}Edges\\ \\'\
        r'\makebox[90pt]{%d\hfill}Connected Components' \
        % (len(adj), epsilon, wGraph.num_edges(), len(cp))

    minx = min([coord[0] for coord in list(adj.keys())])
    maxx = max([coord[0] for coord in list(adj.keys())])
    miny = min([coord[1] for coord in list(adj.keys())])
    maxy = max([coord[1] for coord in list(adj.keys())])

    xpadding = abs(minx - maxx) * 0.1
    ypadding = abs(miny - maxy) * 0.1
    ax.set_xlim(minx - xpadding,
                maxx + xpadding)
    ax.set_ylim(miny - ypadding,
                maxy + ypadding)

    ax.set_aspect('equal')


    ax.plot([0], [0], color='white', label=textstr)

# # Shrink current axis by 20%
#     box = ax.get_position()
#     ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#
# # Put a legend to the right of the current axis
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#
#     box = ax.get_position()
#     ax.set_position([box.x0, box, y0, box.width])

# Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

# Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5)

    if gui:
        return fig
    else:
        show(window)

def plot3d_pc(pointCloud, axes=(0, 1, 2), gui=False, title=False):
    """
    We plot a point cloud.
    """
    if pointCloud.get_space() == 'affine':

        points = pointCloud.get_points()
        xcoords = [p[axes[0]] for p in points]
        ycoords = [p[axes[1]] for p in points]
        if len(points[0]) == 2:
            zcoords = [0 for _ in points]
        else:
            zcoords = [p[axes[2]] for p in points]

        fig = plt.figure()
        ax = Axes3D(fig)

        ax.scatter(xcoords, ycoords, zcoords, marker='.', color='#ff6666')

        fig.set_size_inches(10.0, 10.0)
        if title:
            fig.suptitle(title)

        ax.grid(True)
        ax.set_aspect('equal')

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

#         # Set camera viewpoint
#         # Elevation of camera (default is 30)
#         ax.elev=20
#         # Azimuthal angle of camera (default is 30)
#         ax.azim=30
#         # Camera distance (default is 10)
#         ax.dist=10
#         fig.add_axes(ax)
#         ax.set_aspect('equal')

        if gui:
            return fig
        else:
            plt.show(fig)
#             show(fig)


def set_aspect_equal_3d(ax):
    """Fix equal aspect bug for 3D plots."""
#     print(ax.get_w_lims())
    xlim = ax.get_xlim3d()
    ylim = ax.get_ylim3d()
    zlim = ax.get_zlim3d()

#     print(xlim, ylim, zlim)
    from numpy import mean
    xmean = mean(xlim)
    ymean = mean(ylim)
    zmean = mean(zlim)

    plot_radius = max([abs(lim - mean_)
                       for lims, mean_ in ((xlim, xmean),
                                           (ylim, ymean),
                                           (zlim, zmean))
                       for lim in lims])

#     print(xmean, ymean, zmean, plot_radius)

    ax.set_xlim3d([xmean - plot_radius, xmean + plot_radius])
    ax.set_ylim3d([ymean - plot_radius, ymean + plot_radius])
    ax.set_zlim3d([zmean - plot_radius, zmean + plot_radius])

def set_aspect_equal_3d_2(ax):
    minx = min([coord[0] for coord in list(adj.keys())])
    maxx = max([coord[0] for coord in list(adj.keys())])
    midpointx = (minx + maxx) / 2
    radiusx = abs(maxx - midpointx)
    miny = min([coord[1] for coord in list(adj.keys())])
    maxy = max([coord[1] for coord in list(adj.keys())])
    midpointy = (miny + maxy) / 2
    radiusy = abs(maxy - midpointy)

    ax.set_xlim3d([xmean - plot_radius, xmean + plot_radius])
    ax.set_ylim3d([ymean - plot_radius, ymean + plot_radius])
    ax.set_zlim3d([zmean - plot_radius, zmean + plot_radius])

    zaxis = [coord[2] for coord in list(adj.keys()) if len(coord) > 2]
    if zaxis:
        minz = min(zaxis)
        maxz = max(zaxis)
        midpointz = (minz + maxz) / 2
        radiusz = abs(maxz - minpointz)


def add_color_bar(values, colors):
    components = []
    for vertex, edge in zip(*values):
        components.append('G' + str((vertex, edge)))

    cmap = mpl.colors.ListedColormap(colors)
    cmap.set_over('0.25')
    cmap.set_under('0.75')

#     norm = mpl.colors.BoundaryNorm(bounds, cmapcb.N)
#     cb2 = mpl.colorbar.ColorbarBase(axcb, cmap=cmapcb, norm=norm,
#                                     boundaries=bounds,
#                                     spacing='proportional',
#                                     orientation='horizontal')

#     norm = mpl.colors.Normalize(vmin=min(values), vmax=max(values))
#     norm = mpl.colors.BoundaryNorm(boundaries=values, ncolors=len(values))
#     norm = mpl.colors.LogNorm(vmin=min(values), vmax=max(values))



    sm = plt.cm.ScalarMappable(cmap=cmap)
#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
#     sm.set_array()
    cbar = plt.colorbar(sm, shrink=0.9, pad=0, fraction=0.1)

    ticks = np.linspace(0, 1, len(components)+1)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels(components)
    cbar.set_label("%s largest components G(V, E)" % len(components))



def plot3d_ng(wGraph,
              axes=(0,1,2),
              cmap='Paired',
              method='subdivision',
              save=False,
              title="3D Neighborhood Graph",
              gui=False,
              fancy=True,
              add_colorbar=False):
    """
    For a given epsilon, makes a 3-dimensional plot of a neighborhood
    graph.
    Currently, there are the following cmap options which are selected
    by index:
        0 - Dark2
        1 - Accent
        2 - Paired
        3 - rainbow
        4 - winter
    """


    plt.rc('text', usetex=True)
    plt.rc('font', family='sans-serif: Computer Modern Sans serif')
    plt.axis('off')

#     fig = plt.figure()
    fig, window = create_fig()
    window.wm_title(title)
    ax = Axes3D(fig)
#     axcb = fig.add_axes([0.05, 0.80, 0.9, 0.15])
    if not fancy:
        ax.grid(False)
        ax.set_axis_off()

    epsilon = wGraph.get_epsilon()
    adj = wGraph.get_adjacency()
    cp = wGraph.connected_components()
    cmap = get_cmap(cmap)  # color mappings
    ce = wGraph.connected_edges(padding=3)
#     line_colors = cmap(np.linspace(0, 1, len(ce)))
    line_colors = cmap(np.linspace(0, 1, len(cp)))
    edge_component = {}
#     print(ce)
#     print(type(ce))
    cv = wGraph.connected_vertices(padding=3)

    for i, component in enumerate(cv):
        edge_component[frozenset(ce[i])] = component
#         edge_component[ce[i]] = component[i]



    # [0, 0.1, 0.2 ... 1 ]

    ce.sort(key=len)

    componentIndex = -1
    lines_collection  = []
    import colorsys
    vertex_sizes = []
    edge_sizes = []
    component_colors = []
    for componentIndex, component in enumerate(ce):

        #         scalar = float(len(component)) / numberEdges + 1
        #         tempcomponent = []
        #         for i, edge in enumerate(component):
        #             tempcomponent.append(edge*scalar)
        #         component = set(tempcomponent)
        component = frozenset(component)

        saturation = .5
        lightness = .5
        hue=.5
        rgb_values = colorsys.hls_to_rgb(
            (hue+componentIndex*(3-5**.5)*.5)%1.0,
            saturation,
            lightness)
        lines = a3.art3d.Poly3DCollection(pick_ax_edge(component, axes))
#         lines.set_edgecolor(line_colors[componentIndex])
        lines.set_edgecolor(rgb_values)
        if not edge_sizes or \
                max(edge_sizes) <= len(component):

            if 10 <= len(edge_sizes):
                i = edge_sizes.index(min(edge_sizes))
                vertex_sizes.pop(i)
                edge_sizes.pop(i)
                component_colors.pop(i)

            vertex_sizes.append(len(edge_component[component]))
            edge_sizes.append(len(component))
            component_colors.append(rgb_values)

        ax.add_collection(lines)



    componentIndex += 1

    points = wGraph.singletons(padding=3)
#     point_colors = cmap(np.linspace(0, 1, len(points)))
    if points:
        x, y, z = zip(*[pick_ax(point, axes) for point in \
                        points])
        ax.scatter(x, y, z,
                   marker='.',
                   s=15,
#                    color=point_colors,
                   color=line_colors[:componentIndex],
                   label=r"\makebox[90pt]{%d\hfill}Singletons" % len(x))

    textstr = r'\noindent\makebox[90pt]{%d\hfill}Number of Points\\ \\'\
        r'\makebox[90pt]{%.3f\hfill}Distance\\ \\'\
        r'\makebox[90pt]{%d\hfill}Edges\\ \\'\
        r'\makebox[90pt]{%d\hfill}Connected Components' \
        % (len(adj), epsilon, wGraph.num_edges(), len(cp))

    ax.plot([0], [0], color='white', label=textstr)
    ax.legend(loc='lower left', fontsize='x-large', borderpad=1)

    set_aspect_equal_3d(ax)
    if add_colorbar and \
            2 <= len(edge_sizes):
        add_color_bar((vertex_sizes, edge_sizes), component_colors)


    ax.set_aspect('equal')

    if gui:
        return fig
    else:
        #         plt.show()
        show(window)



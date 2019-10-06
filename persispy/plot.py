"""
AUTHORS:

    - Benjamin Antieau (2015-04)
    - Daniel Etrata (2016-01)

input: pointCloud OR
    wGraph
"""

import numpy as np
# import time

from matplotlib.backends.backend_tkagg \
    import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import mpl_toolkits.mplot3d as a3
from mpl_toolkits.mplot3d import Axes3D
from persispy.point_cloud import PointCloud
from persispy.weighted_simplicial_complex import wGraph
try:  # python3
    import tkinter as tk
except ImportError:  # python2
    import Tkinter as tk
try:
    from persispy.phc import Intersect
except ImportError:
    Intersect = type("None", (object,), {"None": None})
    print("PHCpy is not currently installed. PHC functions are unavailable.")
import matplotlib.pyplot as plt  #noqa - ignore module import level
import matplotlib as mpl  #noqa - ignore module import level


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
        root.winfo_width(), root.winfo_height()  #noqa - tkinter specific

# only time to call pyplot
    fig = plt.figure()
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", destroy)
    root.bind("<Configure>", onsize)
    frame = tk.Frame(root)
    frame.pack(side='top', fill='both', expand=1)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    canvas._tkcanvas.pack(side='top', fill='both', expand=1)  #noqa - tkinter
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


def plot2d_ng(wGraph,
              shading_style='axes',
              axes=(0, 1),
              shading_axis=1,
              method='subdivision',
              title="2D Neighborhood Graph",
              gui=False,
              cmap=0):
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

    adjacency = wGraph.adjacencies()
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
    epsilon = wGraph.epsilon()
    adj = wGraph.adjacencies()
    cp = wGraph.connected_components()
    cmaps = [plt.cm.Dark2, plt.cm.Accent, plt.cm.Paired,
             plt.cm.rainbow, plt.cm.winter]
    cmap = cmaps[cmap]  # color mappings
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


def plot3d_ng(wGraph,
              axes=(0, 1, 2),
              cmap=3,
              method='subdivision',
              save=False,
              title="3D Neighborhood Graph",
              gui=False,
              fancy=True):
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
    if not fancy:
        ax.grid(False)
        ax.set_axis_off()

    epsilon = wGraph.epsilon()
    adj = wGraph.adjacencies()
    cp = wGraph.connected_components()
    cmaps = [plt.cm.Dark2, plt.cm.Accent, plt.cm.Paired,
             plt.cm.rainbow, plt.cm.winter]
    cmap = cmaps[cmap]  # color mappings
    line_colors = cmap(np.linspace(0, 1, len(cp)))

    # [0, 0.1, 0.2 ... 1 ]

    ce = wGraph.connected_edges(padding=3)
    ce.sort(key=len)

    componentIndex = -1
    for componentIndex, component in enumerate(ce):

        vert = pick_ax_edge(component, axes)
        lines = a3.art3d.Poly3DCollection(vert, linewidths=1)

        lines.set_edgecolor(line_colors[componentIndex])

        ax.add_collection(lines)

    componentIndex += 1

    if wGraph.singletons():
        x, y, z = zip(*[pick_ax(point, axes) for point in
                        wGraph.singletons(padding=3)])
        ax.scatter(x, y, z,
                   marker='.',
                   s=15,
                   color=line_colors[componentIndex:],
                   label=r"\makebox[90pt]{%d\hfill}Singletons" % len(x))

    textstr = r'\noindent\makebox[90pt]{%d\hfill}Number of Points\\ \\'\
        r'\makebox[90pt]{%.3f\hfill}Distance\\ \\'\
        r'\makebox[90pt]{%d\hfill}Edges\\ \\'\
        r'\makebox[90pt]{%d\hfill}Connected Components' \
        % (len(adj), epsilon, wGraph.num_edges(), len(cp))

    ax.plot([0], [0], color='white', label=textstr)
    ax.legend(loc='lower left', fontsize='x-large', borderpad=1)

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

    zaxis = [coord[2] for coord in list(adj.keys()) if len(coord) > 2]
    if zaxis:
        minz = min(zaxis)
        maxz = max(zaxis)
        zpadding = abs(minz - maxz) * 0.1
        ax.set_zlim(minz - xpadding,
                    maxz + zpadding)

    ax.set_aspect('equal')

    if gui:
        return fig
    else:
        #         plt.show()
        show(window)

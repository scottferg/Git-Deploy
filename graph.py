import os, sys
import re

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
import cairo

import math

from dulwich.repo import Repo
from dulwich.objects import Commit

# Create a GTK+ widget on which we will draw using Cairo
class Graph(gtk.DrawingArea):
    # Draw in response to an expose-event
    __gsignals__ = {'expose-event': 'override'}

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        context = self.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        context.rectangle(event.area.x, 
                          event.area.y,
                          event.area.width, 
                          event.area.height)
        context.clip()

        self.draw(context, *self.window.get_size())

    def draw(self, context, width, height):
        # Fill the background with gray
        context.set_source_rgb(255, 255, 255)
        context.rectangle(0, 0, width, height)
        context.fill()

        axisColor = []
        axisColor.append([0.47, 0.1, 0.65])
        axisColor.append([0.4, 0.4, 0])
        axisColor.append([0.65, 0.43, 0.1])
        axisColor.append([0.18, 0.05, 0.97])
        axisColor.append([0.4, 0.4, 0])
        axisColor.append([0.65, 0.43, 0.1])
        axisColor.append([0.47, 0.1, 0.65])
        axisColor.append([0.18, 0.05, 0.97])

        setAxisColor = lambda count: context.set_source_rgb(axisColor[count][0],
                                                            axisColor[count][1],
                                                            axisColor[count][2])

        passOffset = 55
        count = 0
        drawnNodeList = []

        print self.commitList
        for index,commit in self.commitList.items():
            setAxisColor(3)

            nodeHeight = height / 2 

            nodeExists = False 

            try:
                ['%s' % x[0] for x in drawnNodeList].index(index)
                print 'Skipping 1: ' + index
            except ValueError:
                lastNode = index 
                print 'Drawing 1: ' + index 
                # Draw commits in black
                context.set_source_rgb(0, 0, 0)
                radius = min(5, 5)
                context.arc(passOffset, nodeHeight, radius, 0, 2 * math.pi)
                currentPos = context.get_current_point()
                context.stroke()
                
                drawnNodeList.append([index, currentPos])
                pass
            

            # TODO: Track each node as it is drawn out, with the
            # coordinates stored within it.  If we come across a node that has
            # already been drawn, don't draw it again.  Connect a curve to
            # it instead.
            # We have to draw the path to the following commits, 
            # and then draw the commits themselves
            verticalOffset = 0 
            useCurve = False

            for path in commit:
                aNodeExists = False 

                for node,pos in drawnNodeList:
                    if node == path:
                        print path + ' exists'
                        aNodeExists = True

                # Reset to the line color
                setAxisColor(0)

                if aNodeExists:
                    position = None

                    print 'Last: ' + lastNode
                    for oldNode in drawnNodeList:
                        if oldNode[0] == lastNode:
                            position = oldNode[1]
                            print oldNode

                    context.move_to(position[0], position[1])
                    context.rel_curve_to(0, 0, 0, -20, -10, -20)
                    print 'Drawing curved ' + path
                else:
                    context.move_to(passOffset + 5, nodeHeight)

                    if not useCurve:
                        context.rel_line_to(10, verticalOffset)
                        print 'Drawing 2: ' + path
                    else:
                        context.rel_curve_to(0, 0, 0, verticalOffset, 10, verticalOffset)
                        print 'Drawing curved ' + path

                    currentPos = context.get_current_point()
                    drawnNodeList.append([path, currentPos])

                context.stroke()

                # Draw commits in black
                context.set_source_rgb(0, 0, 0)
                radius = min(5, 5)
                context.arc(currentPos[0] + 5, currentPos[1], radius, 0, 2 * math.pi)
                context.stroke()

                print path
                lastNode = path
                useCurve = True
                verticalOffset -= 20
                
            context.stroke()
            passOffset += 20

    def __init__(self, commitList):
        super(gtk.DrawingArea, self).__init__()
        self.commitList = commitList 

class Node:
    def getHash(self):
        return self.hash

    def getRefs(self):
        return self.refs

    def getParents(self):
        return self.parents

    def addRef(self, ref):
        self.refs.append(ref)

    def isMerge(self):
        return len(self.parents) > 1

    def __init__(self, hash, parents, refs = []):
        self.hash = hash
        self.parents = parents
        self.refs = refs

    def __cmp__(self, node):
        if isinstance(node, Node):
            return cmp(self.hash, node.getHash())

        return False

    def __repr__(self):
        return "<%s #%s object>" % (self.__class__.__name__, self._id)

def drawCairoGraph(commitList):
    window= gtk.Window()
    window.connect('delete-event', lambda w, q: gtk.main_quit())
    widget = Graph(commitList)
    widget.show()
    window.add(widget)
    window.present()

    gtk.main()

def buildCommitList():

    graph = {'A': ['C'],
             'C': ['D', 'E'],
             'D': ['F'],
             'E': ['F'],
             'F': ['G', 'I'],
             'G': ['H'],
             'H': ['I'],
             'I': ['J'],
             'J': ['I']
            }

    return graph

    repo = Repo(os.getcwd())

    commitList = []

    head = repo.get_refs()['HEAD']
    currentCommit = head

    while repo.get_parents(currentCommit):
        parents = repo.get_parents(currentCommit)
        refs = []

        for ref,hash in repo.get_refs().items():
            if hash == currentCommit:
                refs.append(ref)

        commitList.append(Node(currentCommit, parents, refs))

        currentCommit = parents[0]

    return commitList

if __name__ == '__main__':
    drawCairoGraph(buildCommitList())

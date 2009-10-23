import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
import cairo

import math

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

        self.setAxisColor = lambda count: context.set_source_rgb(axisColor[count][0], axisColor[count][1], axisColor[count][2])

        self.drawnNodes = {}

        for node,children in self.commitList.items():
            self._drawGraph(node, 15, height / 2, context)
            self._drawEdge(node, context)

    def _drawGraph(self, node, offset, height, context, parentNode = None):
        # Iterate over each node in the list
        # If the node has children, recursively pull the child from the
        # overall list, and then draw it's children, and continue to traverse
        # the path.
        # 
        # Log each node and it's coordinates as it is drawn, so that it can be 
        # connected later if necessary
        try:
            self.drawnNodes[node]
            # Node has already been drawn
            return
        except KeyError:
            pass

        # Draw commits in black
        radius = min(5, 5)

        context.set_source_rgb(0, 0, 0)
        context.arc(offset + 5, height / 2, radius, 0, 2 * math.pi)
        # Grab the current position
        self.drawnNodes[node] = (x, y) = context.get_current_point()
        context.stroke()

        # Draw the children
        for child in self.commitList[node]:
            self._drawGraph(child, offset + 20, height, context, node)
            height = height - 50

        return            

    def _getParentNodes(self, node):
        result = []
        
        print node
        for parent,children in self.commitList.items():
            if node in children:
                result.append(parent)
                print result

        return result

    def _drawEdge(self, node, context):
        # Find all nodes that have the current node as a child
        parentNode = self._getParentNodes(node)
        # If we have a parent, connect to it with a line
        if parentNode:
            for parent in parentNode:
                origin = self.drawnNodes[node]
                destination = self.drawnNodes[parent]

                self.setAxisColor(1)

                # If both nodes are at the same height draw a line
                if origin[1] == destination[1]:
                    context.move_to(origin[0] - 10, origin[1])
                    context.line_to(destination[0], destination[1])
                else:
                    context.curve_to(origin[0] - 7, origin[1] + 5, 
                                     origin[0] - 15, origin[1], 
                                     destination[0], destination[1])

                '''
                print 'Current: %s and Y: %s' % (node, origin[1])
                print 'Parent: %s and Y: %s' % (parent, destination[1])
                '''
                context.stroke()

        return context

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
        return '<%s #%s object>' % (self.__class__.__name__, self._id)

def drawCairoGraph(commitList):
    window= gtk.Window()
    window.connect('delete-event', lambda w, q: gtk.main_quit())
    widget = Graph(commitList)
    widget.show()
    window.set_default_size(350, 350)
    window.add(widget)
    window.present()

    gtk.main()

def buildCommitList():

    graph = {'A': ['B'],
             'B': ['C'],
             'C': ['D', 'E'],
             'D': ['F'],
             'E': ['F'],
             'F': ['G'],
             'G': ['H', 'I'],
             'H': ['J'],
             'I': ['J'],
             'J': [],
             'K': []
            }

    return graph

if __name__ == '__main__':
    drawCairoGraph(buildCommitList())

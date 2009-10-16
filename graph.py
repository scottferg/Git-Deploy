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

        passOffset = 15
        count = 0

        for commit in self.commitList:
            setAxisColor(0)

            nodeHeight = height - ((count + 1) * 25)

            # If the commit has more than one parent, fork, otherwise
            # draw a straight line backwards
            if len(commit.getParents()) > 1:
                pass
            else:
                pass
                
            # Draw commits in black
            context.set_source_rgb(0, 0, 0)
            radius = min(5, 5)
            context.arc(passOffset, nodeHeight, radius, 0, 2 * math.pi)
            context.stroke()

            if commit.getRefs():
                setAxisColor(2)
                context.rectangle(passOffset - 5, nodeHeight - 50, 10, 40)
                context.fill_preserve()
                context.set_source_rgb(0, 0, 0)
                context.rectangle(passOffset - 5, nodeHeight - 50, 10, 40)
                context.stroke()

            # Reset to the line color
            setAxisColor(0)
            context.move_to(passOffset - 15, nodeHeight)
            context.rel_line_to(10, 0)
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

    def __init__(self, hash, parents, refs = []):
        self.hash = hash
        self.parents = parents
        self.refs = refs

def drawCairoGraph(commitList):
    window= gtk.Window()
    window.connect('delete-event', lambda w, q: gtk.main_quit())
    widget = Graph(commitList)
    widget.show()
    window.add(widget)
    window.present()

    gtk.main()

'''
Arbitrary change
'''
def buildCommitList():
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

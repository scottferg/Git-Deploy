import os, sys
import re

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
import cairo

import math

pattern = '^(\/|\||\*|\ |\\\)$'

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

        passOffset = 5

        for axis in self.graph:

            count = 0

            for index in axis:
                setAxisColor(count)

                nodeHeight = height - ((count + 1) * 25)

                if index == '|':
                    context.move_to(passOffset - 5, nodeHeight)
                    context.rel_line_to(20, 0)
                elif index == '/':
                    # We are merging out of the source branch, use the merging
                    # branches color
                    setAxisColor(count - 1)
                    context.move_to(passOffset - 20, nodeHeight)
                    context.rel_line_to(35, 45)
                elif index == '\\':
                    # We are merging back to the source branch, use the merging
                    # branches color
                    setAxisColor(count + 1)
                    context.move_to(passOffset - 5, nodeHeight)
                    context.rel_line_to(25, -45)
                elif index == '*':
                    # Draw commits in black
                    context.set_source_rgb(0, 0, 0)
                    radius = min(5, 5)
                    context.arc(passOffset, nodeHeight, radius, 0, 2 * math.pi)
                    context.stroke()
                    # Reset to the line color
                    setAxisColor(count)
                    context.move_to(passOffset + 5, nodeHeight)
                    context.rel_line_to(10, 0)
                
                context.stroke()

                count += 1

            passOffset += 20

    def __init__(self, graph):
        super(gtk.DrawingArea, self).__init__()
        self.graph = graph

def readGitLog():
    process = os.popen('git log --graph --pretty=oneline', 'r')

    sys.stdout.flush()
    
    result = []

    while True:
        commit = process.readline()

        if not commit:
            break

        axisList = []

        for i in commit:

            if not re.search(pattern, i):
                break

            axisList.append(i)

        if axisList:
            result.append(axisList)

    result.reverse()

    return result

def drawCairoGraph():
    window= gtk.Window()
    window.connect('delete-event', lambda w, q: gtk.main_quit())
    widget = Graph(readGitLog())
    widget.show()
    window.add(widget)
    window.present()

    gtk.main()

'''
Arbitrary change
'''
if __name__ == '__main__':
    drawCairoGraph()

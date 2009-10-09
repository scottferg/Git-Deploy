import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

class Graph:

    def onDrawingAreaConfigure(self, widget, event):
        self.graphicsContext = widget.window.new_gc()
        self.colormap = self.graphicsContext.get_colormap()
        self.colors = {}
        self.colors['green'] = self.colormap.alloc_color('green')
        self.colors['white'] = self.colormap.alloc_color('white')

        x, y, width, height = widget.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(widget.window, width, height)

        self.graphicsContext.set_foreground(self.colors['white'])
        self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, width, height)

        self.graphicsContext.set_foreground(self.colors['green'])
        self.pixmap.draw_line(self.graphicsContext, 0, height, 50, height - 100)
        self.pixmap.draw_line(self.graphicsContext, 50, height - 100, 100, height + 100)
        self.pixmap.draw_line(self.graphicsContext, 100, height + 100, 150, height - 100)
        self.pixmap.draw_line(self.graphicsContext, 150, height - 100, 200, height + 100)

        return True

    def onDrawingAreaExpose(self, widget, event):
        x, y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.pixmap, x, y, x, y, width, height)
        return False


    def __init__(self):
        self.drawingArea = gtk.DrawingArea()
        self.drawingArea.set_size_request(350, 350)

        self.drawingArea.connect('configure-event', configure_event)
        self.drawingArea.connect('expose-event', expose_event)

        self.pixmap = None

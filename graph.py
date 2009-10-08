import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

def configure_event(widget, event):
    global pixmap

    graphicsContext = widget.window.new_gc()
    colormap = graphicsContext.get_colormap()
    colors = {}
    colors['green'] = colormap.alloc_color('green')
    colors['white'] = colormap.alloc_color('white')

    x, y, width, height = widget.get_allocation()
    pixmap = gtk.gdk.Pixmap(widget.window, width, height)

    graphicsContext.set_foreground(colors['white'])
    pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, width, height)

    graphicsContext.set_foreground(colors['green'])
    pixmap.draw_line(graphicsContext, 0, 0, width - 100, height - 100)
    pixmap.draw_line(graphicsContext, width - 100, height - 100, width, height - 100)

    return True

def expose_event(widget, event):
    x, y, width, height = event.area
    widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                pixmap, x, y, x, y, width, height)

    return False

win = gtk.Window()


drawingArea = gtk.DrawingArea()
drawingArea.set_size_request(350, 350)

drawingArea.connect('configure-event', configure_event)
drawingArea.connect('expose-event', expose_event)

pixmap = None

win.add(drawingArea)
win.show_all()

gtk.mainloop()

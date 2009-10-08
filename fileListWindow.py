import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

import os, sys

class FileListWindow:

    def onBtnOkayClicked(self, widget, data = None):
        self.window.destroy()
    
    def deleteEvent(self, widget, event, data = None):
        self.window.destroy()

    def __init__(self, fileList):
        # Pull widgets from Glade
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.btnOkay = glade.get_widget('btnOkay')
        self.txtFileList = glade.get_widget('txtFileList')
        self.window = glade.get_widget('fileListWindow')

        # Populate text box
        self.textBuffer = gtk.TextBuffer()
        self.textBuffer.set_text(fileList)
        self.txtFileList.set_buffer(self.textBuffer)

        # Setup callbacks
        self.window.connect('delete_event', self.deleteEvent)
        glade.signal_autoconnect(self)

        # Display the window
        self.window.show_all()

    def main(self):
        gtk.main()

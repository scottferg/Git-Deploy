import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

import observer

import threading
import os,sys

gtk.gdk.threads_init()

class OperationThread(threading.Thread, observer.Subject):
    def __init__(self, operation, params, parent):
        self.operation = operation
        self.params = params
        observer.Subject.__init__(self)
        threading.Thread.__init__(self)
        self.attach(parent)

        # Tell the control that we've started the thread
        self.notify('STARTED')

    def run(self):
        if self.params:
            result = self.operation(self.params)
        else:
            result = self.operation()

        if result:
            self.notify(True)
        else:
            self.notify(False)

class PulseWindowDialog(observer.Observer):
    def update(self, *args):
        print 'Update'
        self.prgOperationProgress.pulse()
        
        if self.prgOperationProgress.get_fraction() == 1.0:
            pass
    
    def show(self):
        print 'Show!'
        # Display the window
        self.window.show_all()

    def __init__(self, operationName, pulse, parent):
        # Pull widgets from Glade
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.prgOperationProgress = glade.get_widget('prgOperationProgress')
        self.lblTitle = glade.get_widget('lblTitle')
        self.window = glade.get_widget('wndOperationDialog')

        self.lblTitle.set_text('<b>%s</b>' % operationName)
        self.lblTitle.set_use_markup(True)

        self.prgOperationProgress.set_pulse_step(pulse)

        glade.signal_autoconnect(self)

class ProgressWindowDialog(observer.Observer):
    def _performOperation(self):
        OperationThread(self.operation, self.param, self).start()

    def onWindowShow(self, widget, data = None):
        self._performOperation()

    def onBtnOkayClicked(self, widget, data = None):
        self.window.destroy()

    def deleteEvent(self, widget, event, data = None):
        self.window.destroy()

    def update(self, *args):
        if args[1] == 'STARTED':
            self.prgOperationProgress.set_fraction(0.25)
        else:
            self.prgOperationProgress.set_fraction(1)
            self.btnOkay.set_sensitive(True)

    def show(self):
        # Display the window
        self.window.show_all()

    def __init__(self, operationName, operation, param = None):
        # Pull widgets from Glade
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.btnOkay = glade.get_widget('btnOkay')
        self.prgOperationProgress = glade.get_widget('prgOperationProgress')
        self.lblTitle = glade.get_widget('lblTitle')
        self.window = glade.get_widget('wndOperationDialog')

        self.window.connect('show', self.onWindowShow)

        self.lblTitle.set_text('<b>%s</b>' % operationName)
        self.lblTitle.set_use_markup(True)

        glade.signal_autoconnect(self)

        self.operation = operation
        self.param = param

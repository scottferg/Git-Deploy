import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

import gitHandler

class MainUI:

    def makeListModel(self):
        '''Create the empty tree store'''
        self.listStore = gtk.ListStore(str, str)
        return

    def getListModel(self):
        '''Returns the list model'''
        if self.listStore:
            return self.listStore
        else:
            return None

    def addCommit(self, hash):
        '''Add a commit to the list'''
        message = gitHandler.getCommitMessage(hash)

        if message:
            self.listStore.append([hash, message])
        return

    def makeListView(self, model):
        '''Initialize the empty list'''
        self.treeView = gtk.TreeView(model)

        self.idRenderer = gtk.CellRendererText()
        self.commitRenderer = gtk.CellRendererText()
        self.descriptionRenderer = gtk.CellRendererText()

        self.column0 = gtk.TreeViewColumn('id', self.idRenderer, text = 0)
        self.column0.set_visible(False)

        self.column1 = gtk.TreeViewColumn('Commit', self.commitRenderer, text = 0)
        self.column1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.column1.set_expand(False)

        self.column2 = gtk.TreeViewColumn('Description', self.descriptionRenderer, text = 1)
        self.column2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.column2.set_expand(True)

        self.treeView.append_column(self.column0)
        self.treeView.append_column(self.column1)
        self.treeView.append_column(self.column2)
        self.treeView.set_expander_column(self.column2)
        self.treeView.set_rules_hint(True)

        return self.treeView
    
    def onBtnOkayClicked(self, widget, data = None):
        self.addCommit(self.txtCommitEntry.get_text())
        self.txtCommitEntry.set_text('')
        return

    def deleteEvent(self, widget, event, data = None):
        gtk.main_quit()
        return

    def destroy(self, widget, data = None):
        gtk.main_quit()
        return

    def __init__(self):
        # Pull widgets from Glade
        glade = gtk.glade.XML('glade/mainWindow.glade')

        self.btnOkay = glade.get_widget('btnOkay')
        self.txtCommitEntry = glade.get_widget('txtCommitEntry')
        self.listViewBox = glade.get_widget('listViewBox')
        self.window = glade.get_widget('mainWindow')

        # Initialize the treestore
        self.makeListModel()
        self.model = self.getListModel()
        self.treeView = self.makeListView(self.model)

        self.listViewBox.pack_start(self.treeView)

        # Attach event handlers
        self.window.connect('delete_event', self.deleteEvent)
        glade.signal_autoconnect(self)

        # Display the window
        self.window.show_all()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    window = MainUI()
    window.main()

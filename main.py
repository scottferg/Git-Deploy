import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

import os, sys

import gitHandler
import fileListWindow

class MainUI:

    def checkCommitInList(self, commit):
        for row in self.listStore:
            if row[0] == commit:
                return True

        return False

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

        commit = gitHandler.getCommitMessage(hash)

        # Don't add a commit twice
        if not self.checkCommitInList(commit['hash'][:10]):
            # Nitpicky formatting, even though 'head' will still
            # work
            if hash.upper() == 'HEAD':
                hash = 'HEAD'
            else:
                hash = hash.lower()

            if commit:
                self.listStore.append([commit['hash'][:10], 
                commit['message']])
            else:
                # TODO: Pop an alert here
                pass

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
        self.column1.set_min_width(90)
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
    
    def onBtnAddClicked(self, widget, data = None):
        '''Handler for okay button'''
        self.addCommit(self.txtCommitEntry.get_text())
        self.txtCommitEntry.set_text('')
        return

    def onBtnDisplayListClicked(self, widget, data = None):
        '''Handler for display button'''

        # TODO: This should be threaded

        commitList = []
        fileList = []

        commitList.extend(['%s' % row[0] for row in self.listStore])

        for commit in commitList:
            result = gitHandler.findChangedFiles(commit)

            # Don't add the same filename twice
            for file in result:
                try:
                    fileList.index(file)
                except ValueError:
                    # If the file is not found, add it to the list
                    fileList.append(file)

        self.fileListWindow = fileListWindow.FileListWindow('\n'.join(['%s' % x for x in fileList]))

        return

    def onTxtCommitEntryKeyDown(self, widget, event, data = None):
        if event.keyval == 65293:
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
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.btnAdd = glade.get_widget('btnAdd')
        self.btnDisplayList = glade.get_widget('btnDisplayList')
        self.txtCommitEntry = glade.get_widget('txtCommitEntry')
        self.wndScrolledWindow = glade.get_widget('wndScrolledWindow')
        self.window = glade.get_widget('mainWindow')

        # Initialize the treestore
        self.makeListModel()
        self.model = self.getListModel()
        self.treeView = self.makeListView(self.model)

        # Add it to the scrollable window
        self.wndScrolledWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.wndScrolledWindow.add_with_viewport(self.treeView)

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

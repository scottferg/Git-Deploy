#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

import os, sys
import getopt

import gitHandler
import fileListWindow

class MainUI:

    def _checkCommitInList(self, commit):
        '''
        Check whether or not a commit is already in the
        list.
        '''
        for row in self.listStore:
            if row[0] == commit:
                return True

        return False

    def _addCommit(self, hash):
        '''
        Add a commit to the list
        '''
        commit = gitHandler.getCommitMessage(hash)

        # Don't add a commit twice
        if not self._checkCommitInList(commit['hash'][:10]):
            # Nitpicky formatting, even though 'head' will still
            # work
            if hash.upper() == 'HEAD':
                hash = 'HEAD'
            else:
                hash = hash.lower()

            if commit:
                self.listStore.prepend([commit['hash'][:10], 
                commit['message']])
            else:
                # TODO: Pop an alert here
                pass

        return

    def _getFormattedDiffBuffer(self, commit):

        textBuffer = gtk.TextBuffer()
        textBuffer.set_text(gitHandler.getCommitDiff(commit))

        startIter, endIter = textBuffer.get_bounds()

        # Setup text formatting tags
        tagTable = textBuffer.get_tag_table()

        defaultTag = gtk.TextTag('default')
        defaultTag.set_property('font', 'Courier')
        defaultTag.set_property('foreground', '#666666')
        defaultTag.set_property('background', '#ffffff')

        addTag = gtk.TextTag('add')
        addTag.set_property('font', 'Courier')
        addTag.set_property('foreground', '#666633')
        addTag.set_property('background', '#66cc66')

        removeTag = gtk.TextTag('remove')
        removeTag.set_property('font', 'Courier')
        removeTag.set_property('foreground', '#660000')
        removeTag.set_property('background', '#ff3333')

        tagTable.add(defaultTag)
        tagTable.add(addTag)
        tagTable.add(removeTag)

        textBuffer.apply_tag(defaultTag, startIter, endIter)
        
        # Read each line and style it accordingly
        lineCount = textBuffer.get_line_count()
        count = 0

        while (count < lineCount):
            count += 1
            currentIter = textBuffer.get_iter_at_line(count)

            try:
                currentEndIter = textBuffer.get_iter_at_line(count + 1)
                
                if currentIter.get_text(currentEndIter)[0] == '+':
                    textBuffer.apply_tag(addTag, currentIter, currentEndIter)
                elif currentIter.get_text(currentEndIter)[0] == '-':
                    textBuffer.apply_tag(removeTag, currentIter, currentEndIter)
            except TypeError:
                pass

        return textBuffer

    def _makeListModel(self):
        '''
        Create the empty tree store
        '''
        self.listStore = gtk.ListStore(str, str)
        return

    def _getListModel(self):
        '''
        Returns the list model
        '''
        if self.listStore:
            return self.listStore
        else:
            return None

    def _makeListView(self, model):
        '''
        Initialize the empty list
        '''
        self.treeView = gtk.TreeView(model)

        self.idRenderer = gtk.CellRendererText()
        self.commitRenderer = gtk.CellRendererText()
        self.descriptionRenderer = gtk.CellRendererText()

        self.commitColumn = gtk.TreeViewColumn('Commit', self.commitRenderer, text = 0)
        self.commitColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.commitColumn.set_min_width(90)
        self.commitColumn.set_expand(False)

        self.descriptionColumn = gtk.TreeViewColumn('Description', self.descriptionRenderer, text = 1)
        self.descriptionColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.descriptionColumn.set_expand(True)

        self.treeView.append_column(self.commitColumn)
        self.treeView.append_column(self.descriptionColumn)
        self.treeView.set_expander_column(self.descriptionColumn)
        self.treeView.set_rules_hint(True)

        return self.treeView
    
    def onBtnAddClicked(self, widget, data = None):
        '''
        Handler for okay button
        '''
        self._addCommit(self.txtCommitEntry.get_text())
        self.txtCommitEntry.set_text('')
        return

    def onBtnDisplayListClicked(self, widget, data = None):
        '''
        Handler for display button
        '''
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

        self.fileListWindow = fileListWindow.FileListWindow('\n'.join(['%s' % x for x in sorted(fileList)]))

        return

    def onTxtCommitEntryKeyDown(self, widget, event, data = None):
        if event.keyval == 65293:
            self._addCommit(self.txtCommitEntry.get_text())
            self.txtCommitEntry.set_text('')

        return

    def onCommitSelected(self, widget, data = None):
        (model, iter) = widget.get_selected()
        commit = model.get_value(iter, 0)

        # Display the buffer
        self.txtDiffView.set_buffer(self._getFormattedDiffBuffer(commit))

    def __init__(self, *args):
        # Pull widgets from Glade
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.btnAdd = glade.get_widget('btnAdd')
        self.btnDisplayList = glade.get_widget('btnDisplayList')
        self.txtCommitEntry = glade.get_widget('txtCommitEntry')
        self.txtDiffView = glade.get_widget('txtDiffView')
        self.wndScrolledWindow = glade.get_widget('wndScrolledWindow')
        self.window = glade.get_widget('mainWindow')

        # Initialize the treestore
        self._makeListModel()
        self.model = self._getListModel()
        self.treeView = self._makeListView(self.model)

        # Initialize tree view selector
        self.selectedCommit = self.treeView.get_selection()
        self.selectedCommit.set_mode(gtk.SELECTION_SINGLE)

        # Add it to the scrollable window
        self.wndScrolledWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.wndScrolledWindow.add_with_viewport(self.treeView)

        # Attach event handlers
        self.selectedCommit.connect('changed', self.onCommitSelected)
        self.window.connect('delete_event', lambda w, q: gtk.main_quit())
        glade.signal_autoconnect(self)

        # Display the window
        self.window.show_all()

        if args:
            commitList = gitHandler.getCommitsSinceTag(args[0])
            for commit in commitList:
                self._addCommit(commit)

    def main(self):
        gtk.main()

def parseCommandLineArguments():
    argList = None

    options, remainder = getopt.getopt(sys.argv[1:], 't:c:', ['tag=','commit=']);

    for opt, arg in options:
        if (opt in ('-t', '--tag')):
            tag = arg
        if (opt in ('-c', '--commit')):
            tag = arg

    if tag:
        window = MainUI(tag)
    else:
        window = MainUI()
        
    window.main()

if __name__ == '__main__':
    parseCommandLineArguments()

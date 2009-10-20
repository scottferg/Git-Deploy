#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
import pango

import os, sys
import getopt
import threading

import gitHandler
import fileListWindow
import observer

gobject.threads_init()

class StatusThread(threading.Thread, observer.Subject):
    def __init__(self, hashList, parent):
        self.hashList = hashList
        threading.Thread.__init__(self)
        observer.Subject.__init__(self)
        self.attach(parent)

    def run(self):
        for hash in self.hashList:
            result = gitHandler.cherryPickCommit(hash, True)

            if result:
                self.notify(True, hash)
            else:
                self.notify(False, hash)

        gitHandler.cleanBranch()

class MainUI(observer.Observer):

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
        try:
            commit = gitHandler.getCommitMessage(hash)

            # Don't add a commit twice
            if not self._checkCommitInList(commit['hash'][:10]):
                if commit:
                    self.listStore.prepend([commit['hash'][:10], 
                                            commit['message'],
                                            gtk.STOCK_REFRESH,
                                            commit['author'],
                                            commit['date']
                                            ])
                else:
                    # TODO: Pop an alert here
                    pass
        except:
            pass

        return

    def _checkCommitStatus(self):
        iter = self.listStore.get_iter_first()
        hashList = []

        while iter:
            hashList.append(self.listStore.get_value(iter, 0))

            iter = self.listStore.iter_next(iter)
        
        StatusThread(hashList, self).start()

    def _getFormattedDiffBuffer(self, commit):
        '''
        Formats a commit diff message with proper styling
        '''
        textBuffer = gtk.TextBuffer()
        textBuffer.set_text(commit)

        startIter, endIter = textBuffer.get_bounds()

        # Setup text formatting tags
        tagTable = textBuffer.get_tag_table()

        defaultTag = gtk.TextTag('default')
        defaultTag.set_property('font', 'Courier')
        defaultTag.set_property('foreground', '#003399')
        defaultTag.set_property('paragraph-background', '#ffffff')

        addTag = gtk.TextTag('add')
        addTag.set_property('font', 'Courier')
        addTag.set_property('foreground', '#666600')
        addTag.set_property('paragraph-background', '#99ff66')

        removeTag = gtk.TextTag('remove')
        removeTag.set_property('font', 'Courier')
        removeTag.set_property('foreground', '#cc0033')
        removeTag.set_property('paragraph-background', '#ffcccc')

        patchTag = gtk.TextTag('patch')
        patchTag.set_property('font', 'Courier')
        patchTag.set_property('foreground', '#ffffff')
        patchTag.set_property('paragraph-background', '#003399')

        fileTag = gtk.TextTag('file')
        fileTag.set_property('font', 'Courier')
        fileTag.set_property('foreground', '#ffffff')
        fileTag.set_property('paragraph-background', '#cc6600')

        tagTable.add(defaultTag)
        tagTable.add(addTag)
        tagTable.add(removeTag)
        tagTable.add(patchTag)
        tagTable.add(fileTag)

        textBuffer.apply_tag(defaultTag, startIter, endIter)
        
        # Read each line and style it accordingly
        lineCount = textBuffer.get_line_count()
        count = 0

        while (count < lineCount):
            count += 1
            currentIter = textBuffer.get_iter_at_line(count)

            try:
                currentEndIter = textBuffer.get_iter_at_line(count + 1)

                if currentIter.get_text(currentEndIter)[0:1] == '+':
                    textBuffer.apply_tag(addTag, currentIter, currentEndIter)
                elif currentIter.get_text(currentEndIter)[0:1] == '-':
                    textBuffer.apply_tag(removeTag, currentIter, currentEndIter)
                elif currentIter.get_text(currentEndIter)[0:2] == '@@':
                    textBuffer.apply_tag(patchTag, currentIter, currentEndIter)
                elif currentIter.get_text(currentEndIter)[0:4] == 'diff':
                    nextLineIter = textBuffer.get_iter_at_line(count + 4)
                    textBuffer.apply_tag(fileTag, currentIter, nextLineIter)
            except TypeError:
                pass

        return textBuffer

    def _makeListModel(self):
        '''
        Create the empty tree store
        '''
        self.listStore = gtk.ListStore(str, str, str, str, str)
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

        self.commitRenderer = gtk.CellRendererText()
        self.descriptionRenderer = gtk.CellRendererText()
        self.indicatorRenderer = gtk.CellRendererPixbuf()
        self.authorRenderer = gtk.CellRendererText()
        self.dateRenderer = gtk.CellRendererText()

        self.commitColumn = gtk.TreeViewColumn('Commit', self.commitRenderer, text = 0)
        self.commitColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.commitColumn.set_expand(False)

        self.descriptionColumn = gtk.TreeViewColumn('Description', self.descriptionRenderer, text = 1)
        self.descriptionColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.descriptionColumn.set_expand(True)

        self.indicatorColumn = gtk.TreeViewColumn('Current status', self.indicatorRenderer, stock_id = 2)
        self.indicatorColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.indicatorColumn.set_expand(False)

        self.authorColumn = gtk.TreeViewColumn('Author', self.authorRenderer, text = 3)
        self.authorColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.authorColumn.set_expand(False)

        self.dateColumn = gtk.TreeViewColumn('Date', self.dateRenderer, text = 4)
        self.dateColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.dateColumn.set_expand(False)

        self.treeView.append_column(self.commitColumn)
        self.treeView.append_column(self.descriptionColumn)
        self.treeView.append_column(self.indicatorColumn)
        self.treeView.append_column(self.authorColumn)
        self.treeView.append_column(self.dateColumn)
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

        diffText = 'Author: ' + gitHandler.findCommitAuthor(commit) + ' (' 
        diffText += gitHandler.findCommitAuthoredDate(commit) + ')\n'
        diffText += 'Committer: ' + gitHandler.findCommitCommitter(commit) + ' ('
        diffText += gitHandler.findCommitCommittedDate(commit) + ')\n'
        diffText += 'Parent: ' + gitHandler.findParentCommit(commit) + '\n\n'
        diffText += gitHandler.getCommitDiff(commit)

        # Display the buffer
        self.txtDiffView.set_buffer(self._getFormattedDiffBuffer(diffText))

    def onCommitClicked(self, widget, event):
        if event.button == 3:
            pathInfo = self.treeView.get_path_at_pos(int(event.x), int(event.y))
            
            if pathInfo is not None:
                path,col,cellx,celly = pathInfo
                self.treeView.grab_focus()
                self.treeView.set_cursor(path, col, 0)
                self.commitContext.popup(None, None, None, event.button, event.time)
            
            return True

    def update(self, *args):
        status = gtk.STOCK_DIALOG_ERROR
    
        if args[1]:
            status = gtk.STOCK_APPLY

        iter = self.listStore.get_iter_first()

        # Find the commit in the list, and set the status
        while iter:
            currentHash = self.listStore.get_value(iter, 0)

            if currentHash == args[2]:
                self.listStore.set_value(iter, 2, status)
                break
            
            iter = self.listStore.iter_next(iter)

    def __init__(self, *args):
        # Pull widgets from Glade
        glade = gtk.glade.XML(os.path.abspath(sys.path[0]) + '/glade/mainWindow.glade')

        self.btnAdd = glade.get_widget('btnAdd')
        self.btnDisplayList = glade.get_widget('btnDisplayList')
        self.txtCommitEntry = glade.get_widget('txtCommitEntry')
        self.txtDiffView = glade.get_widget('txtDiffView')
        self.lblCurrentRef = glade.get_widget('lblCurrentRef')
        self.wndScrolledWindow = glade.get_widget('wndScrolledWindow')
        self.graphWindow = glade.get_widget('graphWindow')
        self.commitContext = glade.get_widget('commitContext')
        self.window = glade.get_widget('mainWindow')

        # Display the current ref
        self.lblCurrentRef.set_text('<b>' + self.lblCurrentRef.get_text() + '</b> ' + gitHandler.getCurrentRef())
        self.lblCurrentRef.set_use_markup(True)

        # Initialize the treestore
        self._makeListModel()
        self.model = self._getListModel()
        self.treeView = self._makeListView(self.model)

        # Initialize tree view selector
        self.selectedCommit = self.treeView.get_selection()
        self.selectedCommit.set_mode(gtk.SELECTION_SINGLE)

        # Setup context menu for commit list
        menuItem = gtk.MenuItem('Cherry-pick this commit')
        self.commitContext.append(menuItem)
        menuItem.show()
        menuItem = gtk.MenuItem('Revert this commit')
        self.commitContext.append(menuItem)
        menuItem.show()

        # Add it to the scrollable window
        self.wndScrolledWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.wndScrolledWindow.add_with_viewport(self.treeView)

        # self.graphWindow.add_with_viewport(graph.Graph(graph.readGitLog()))

        # Attach event handlers
        self.selectedCommit.connect('changed', self.onCommitSelected)
        self.treeView.connect('button_press_event', self.onCommitClicked)
        self.window.connect('delete_event', lambda w, q: gtk.main_quit())
        glade.signal_autoconnect(self)

        # Display the window
        self.window.show_all()

        # Parse command line arguments
        if args:
            if args[0][0] == 'tag':
                pass
                for commit in gitHandler.getCommitsSinceTag(args[0][1]):
                    self._addCommit(commit)
            elif args[0][0] == 'commit':
                self._addCommit(args[0][1])
            elif args[0][0] == 'branch':
                for commit in gitHandler.getBranch(args[0][1]):
                    self._addCommit(commit)

        self._checkCommitStatus()

    def main(self):
        gtk.main()

def parseCommandLineArguments():
    argList = []

    options, remainder = getopt.getopt(sys.argv[1:], 't:c:b:', ['tag=','commit=','branch=']);

    for opt, arg in options:
        if (opt in ('-t', '--tag')):
            argList.append('tag')
            argList.append(arg)            
        if (opt in ('-c', '--commit')):
            argList.append('commit')
            argList.append(arg)            
        if (opt in ('-b', '--branch')):
            argList.append('branch')
            argList.append(arg)            

    if argList:
        window = MainUI(argList)
    else:
        window = MainUI()
        
    window.main()

if __name__ == '__main__':
    parseCommandLineArguments()

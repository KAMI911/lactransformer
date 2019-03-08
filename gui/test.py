#!/bin/python
"""
Hello World, but with more meat.
"""

import wx

SUPPORTED_FILETYPES = 'LAS Point Cloud files (*.las)|*.las|' \
                      'TXT Point Clod files (*.txt)|*.txt|' \
                      'TerraPhoto Image list files (*.iml)|*.iml|' \
                      'Riegl Camera CSV files (*.csv)|*.csv|' \
                      'Riegl PEF files (*.pef)|*.pef'

app_name = 'LAC Transformer'

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        panel = wx.Panel(self)

        fileMainMngSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileMngSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileMngButtonSizer = wx.BoxSizer(wx.VERTICAL)

        addFileButton = wx.Button(panel, 11, "Add a file", style=wx.BU_EXACTFIT, size=(120, 30))
        fileMngButtonSizer.Add(addFileButton, 0, wx.ALIGN_LEFT|wx.ALL,2)
        addDirectoryButton = wx.Button(panel, 12, "Add a directory", style=wx.BU_EXACTFIT, size=(120, 30))
        fileMngButtonSizer.Add(addDirectoryButton, 0, wx.ALIGN_LEFT|wx.ALL,2)
        removeSelectedButton = wx.Button(panel, 13, "Remove selected", style=wx.BU_EXACTFIT, size=(120, 30))
        fileMngButtonSizer.Add(removeSelectedButton, 0, wx.ALIGN_LEFT|wx.ALL,2)
        removeAllButton = wx.Button(panel, 14, "Remove all", style=wx.BU_EXACTFIT, size=(120, 30))
        fileMngButtonSizer.Add(removeAllButton, 0, wx.ALIGN_LEFT|wx.ALL,2)
        #self.SetSizer(fileMngButtonSizer)
        fileMngButtonSizer.Fit(self)

        #fileListBox = wx.ListBox(panel, 5, style=wx.LB_NEEDED_SB|wx.LB_EXTENDED|wx.LB_SORT, size=(300, 300))
        #fileMngSizer.Add(fileListBox, 0, wx.ALIGN_LEFT|wx.EXPAND)


        #self.dirPicker = wx.DirPickerCtrl (self, id=wx.ID_ANY, style=wx.DIRP_DIR_MUST_EXIST | wx.DIRP_USE_TEXTCTRL)


        fileMainMngSizer.Add(fileMngButtonSizer, 0, wx.ALIGN_LEFT, 0)
        fileMainMngSizer.Add(fileMngSizer, 0, wx.ALIGN_LEFT|wx.EXPAND, 0)

        #fileMngSizer.Fit(self)
        fileMainMngSizer.SetSizeHints(self)
        self.SetSizer(fileMainMngSizer)
        fileMainMngSizer.Fit(self)

        files = ['filea','file1','fileb','file6','file4','filed','filec']
        #for i, file in enumerate(files):
        #    fileListBox.Append(file)
        #Add(self.btn, 0, wx.ALIGN_CENTER)
        #self.btn.Bind(wx.EVT_BUTTON, self.OnClicked)


class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageTwo object", (40,40))

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageThree object", (60,60))

class HelloFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)
        icon_path = 'res/eagle_small.png'
        self.SetIcon(wx.Icon(icon_path))

        # create a panel in the frame
        pnl = wx.Panel(self)
        # Here we create a panel and a notebook on the panel
        nb = wx.Notebook(pnl)

        # create the page windows as children of the notebook
        page1 = PageOne(nb)
        page2 = PageTwo(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Files")
        nb.AddPage(page2, "Settings")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        #self.__set_properties()
        #self.__do_layout()
        status_data = {'app_name': app_name}
        self.SetStatusText("Welcome to the {app_name} application!".format(**status_data))


    def __do_layout(self):
        # begin wxGlade: frame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.notebook_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        openfileItem = fileMenu.Append(-1, "&Open file...\tCtrl-O",
                "Open an supported file")
        opendirectoryItem = fileMenu.Append(-1, "Open &directory...\tCtrl-Shift-O",
                "Open a dircetory with supportted files")
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnOpenFile, openfileItem)
        self.Bind(wx.EVT_MENU, self.OnOpenDirectory, opendirectoryItem)
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnOpenFile(self, event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0, 0, 200, 50)

        openFileDialog = wx.FileDialog(frame, "Open an supported file", "", "",
                                       SUPPORTED_FILETYPES,
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        openFileDialog.ShowModal()
        print(openFileDialog.GetPath())
    def OnOpenDirectory(self, event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0, 0, 200, 50)

        openFileDialog = wx.DirDialog(frame, "Open a dircetory with supportted files", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        openFileDialog.ShowModal()
        print(openFileDialog.GetPath())

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython based GUI that helps to configure LAC Transformer command line tool. LAC Transformer command line tool transforms LAS and TXT Point Clouds, Riegl CSV and PEF files between supported projections.",
                      "About LAC Transformer application",
                      wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='LAC Transformer')
    frm.Show()
    app.MainLoop()
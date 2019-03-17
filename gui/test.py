#!/bin/python

import glob
import os

import wx

SUPPORTED_FILETYPES = 'LAS Point Cloud files (*.las)|*.las|' \
                      'TXT Point Clod files (*.txt)|*.txt|' \
                      'TerraPhoto Image list files (*.iml)|*.iml|' \
                      'Riegl Camera CSV files (*.csv)|*.csv|' \
                      'Riegl PEF files (*.pef)|*.pef'

app_name = 'LAC Transformer'

class PageFiles(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        panel = wx.Panel(self)

        self.list_ctrl = wx.ListCtrl(self,
                                     style=wx.LC_REPORT
                                     |wx.BORDER_SUNKEN
                                     )
        self.list_ctrl.InsertColumn(0, 'Filename')

        addFileButton = wx.Button(self, label="Add a file")
        addFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        addDirectoryButton = wx.Button(self, label="Add a Folder")
        addDirectoryButton.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        removeSelectedButton = wx.Button(self, label="Remove selected")
        removeSelectedButton.Bind(wx.EVT_BUTTON, self.onRemoveSelected)
        removeAllButton = wx.Button(self, label="Remove all")
        removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAll)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer.Add(addFileButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(addDirectoryButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(removeSelectedButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(removeAllButton, 0, wx.ALL|wx.CENTER, 2)

        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)


    def onOpenFile(self, event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0, 0, 200, 50)

        dlg = wx.FileDialog(frame, "Open an supported file", "", "",
                                       SUPPORTED_FILETYPES,
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.updateDisplay(path)
        dlg.Destroy()


    def onOpenDirectory(self, event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0, 0, 200, 50)

        dlg = wx.DirDialog(frame, "Open a dircetory with supportted files", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.updateDisplay(path)
        dlg.Destroy()


    def updateDisplay(self, folder_path):
        """
        Update the listctrl with the file names in the passed in folder
        """
        paths = glob.glob(folder_path + "/*.*")
        for index, path in enumerate(paths):
            self.list_ctrl.InsertStringItem(index, os.path.basename(path))


    def onRemoveSelected(self, event):
        pass


    def onRemoveAll(self, event):
        self.list_ctrl.DeleteAllItems()


class PageSettings(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        button_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Projection')
        process_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Process')
        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer.Add(wx.StaticText(self, -1, 'Input projection'), 0, wx.ALL|wx.CENTER|wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.Choice(self, choices=['EOV', 'WGS84'], name='Input projection'), 0, wx.ALL | wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.StaticText(self, -1, 'Output projection'), 0, wx.ALL|wx.CENTER|wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.Choice(self, choices=['EOV', 'WGS84'], name='Output projection'), 0, wx.ALL | wx.ALIGN_LEFT, 5)
        process_sizer.Add(wx.StaticText(self, -1, 'Cores'), 0, wx.ALL|wx.CENTER, 5)
        process_number = wx.Slider(self, minValue=1, maxValue=16, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS|wx.SL_BOTTOM, size=(200,50), name='Cores')
        # Using EVT_SCROLL_CHANGED instead of EVT_SLIDER. It is running on Linux (as doc says it is Windows only), and emit only the last change.
        process_number.Bind(wx.EVT_SCROLL_CHANGED, self.sliderProcessEvent)
        process_sizer.Add(process_number, 0, wx.ALL|wx.EXPAND, 2)

        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(process_sizer, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)

    def sliderProcessEvent(self, event):
        value = event.GetEventObject().GetValue()
        print ('Label of pressed button = {}'.format(value))


class PageProcess(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        process_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Process controll')
        progress_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Progress')
        logger_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Console output')
        sizer = wx.BoxSizer(wx.VERTICAL)

        startProcess = wx.Button(self, label='Start process')
        startProcess.Bind(wx.EVT_BUTTON, self.startProcessEvent)
        stopProcess = wx.Button(self, label='Stop process')
        stopProcess.Bind(wx.EVT_BUTTON, self.stopProcessEvent)
        process_sizer.Add(startProcess, 0, wx.ALL|wx.CENTER, 5)
        process_sizer.Add(stopProcess, 0, wx.ALL|wx.CENTER, 5)

        progressBar = wx.Gauge(self, id=0, size=(400, 50), style=wx.GA_HORIZONTAL, range=100, name='Progress')
        progress_sizer.Add(progressBar, 1, wx.ALL|wx.EXPAND, 5)

        log_control = wx.TextCtrl(self, wx.NewId(), size=(4000,4000), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2|wx.TE_AUTO_URL|wx.TE_LEFT|wx.TE_BESTWRAP)
        logger_sizer.Add(log_control, 1, wx.ALL|wx.EXPAND, 5)

        sizer.Add(process_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(progress_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(logger_sizer, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        print(progressBar.GetValue())
        print(progressBar.GetRange())
        progressBar.SetValue(60)
        print(progressBar.GetValue())

        log_control.LoadFile(os.path.join('/', 'common', 'git', 'lactransformer', 'lactransformer_20190312_205956.log'))

    def startProcessEvent(self, event):
        btn = event.GetEventObject().GetLabel()
        print ('Label of pressed button = {}'.format(btn))

    def stopProcessEvent(self, event):
        btn = event.GetEventObject().GetLabel()
        print ('Label of pressed button = {}'.format(btn))

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
        pageFiles = PageFiles(nb)
        pageSettings = PageSettings(nb)
        pageProcess = PageProcess(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(pageSettings, 'Settings')
        nb.AddPage(pageFiles, 'Files')
        nb.AddPage(pageProcess, 'Process')

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

        dlg = wx.DirDialog(frame, "Open a dircetory with supportted files", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.updateDisplay(path)
        dlg.Destroy()


    def updateDisplay(self, folder_path):
        """
        Update the listctrl with the file names in the passed in folder
        """
        paths = glob.glob(folder_path + "/*.*")
        for index, path in enumerate(paths):
            self.list_ctrl.InsertStringItem(index, os.path.basename(path))
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
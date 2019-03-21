#!/bin/python

import glob
import os
import wx
import textwrap
import logging
import datetime
import math
import multiprocessing
import _thread

from lactransformer.libs import Logging, FileListWithProjection, TransformerWorkflow

SUPPORTED_FILETYPES = 'LAS Point Cloud files (*.las)|*.las|' \
                      'TXT Point Clod files (*.txt)|*.txt|' \
                      'TerraPhoto Image list files (*.iml)|*.iml|' \
                      'Riegl Camera CSV files (*.csv)|*.csv|' \
                      'Riegl PEF files (*.pef)|*.pef'

app_name = 'LAC Transformer'
script_path = __file__

# Logging related global settings
logfile_path = os.path.join(os.path.dirname(os.path.dirname(script_path)), 'log')
logfilename = 'lactransformer_{0}.log'.format(datetime.datetime.today().strftime('%Y%m%d_%H%M%S'))
Logging.SetLogging(os.path.join(logfile_path, logfilename))

script_header = textwrap.dedent('''LAS & Co Transformer''')
__version__ = '0.0.0.6'


class PageFiles(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        panel = wx.Panel(self)

        self.list_ctrl = wx.ListCtrl(self,
                                     style=wx.LC_REPORT
                                     |wx.BORDER_SUNKEN
                                     )
        self.list_ctrl.InsertColumn(0, 'Filename')

        self.addFileButton = wx.Button(self, label="Add a file")
        self.addFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.addDirectoryButton = wx.Button(self, label="Add a Folder")
        self.addDirectoryButton.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        self.removeSelectedButton = wx.Button(self, label="Remove selected")
        self.removeSelectedButton.Enable(False)
        self.removeSelectedButton.Bind(wx.EVT_BUTTON, self.onRemoveSelected)
        self.removeAllButton = wx.Button(self, label="Remove all")
        self.removeAllButton.Enable(False)
        self.removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAll)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer.Add(self.addFileButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(self.addDirectoryButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(self.removeSelectedButton, 0, wx.ALL|wx.CENTER, 2)
        button_sizer.Add(self.removeAllButton, 0, wx.ALL|wx.CENTER, 2)

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
        # If list control has elements we enable the remove buttons
        self.updateElemCountDependent()

    def onRemoveSelected(self, event):
        self.updateElemCountDependent()
        pass

    def onRemoveAll(self, event):
        self.list_ctrl.DeleteAllItems()
        self.updateElemCountDependent()

    def updateElemCountDependent(self):
        if self.list_ctrl.GetItemCount() > 0:
            self.removeSelectedButton.Enable(True)
            self.removeAllButton.Enable(True)
        else:
            self.removeSelectedButton.Enable(False)
            self.removeAllButton.Enable(False)


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
        self.max_filenumber = 0
        self.current_filenumber = 0
        wx.Panel.__init__(self, parent)

        process_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Process controll')
        progress_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Progress')
        logger_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Console output')
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.startProcess = wx.Button(self, label='Start process')
        self.startProcess.Bind(wx.EVT_BUTTON, self.startProcessEvent)
        self.stopProcess = wx.Button(self, label='Stop process')
        self.stopProcess.Enable(False)
        self.stopProcess.Bind(wx.EVT_BUTTON, self.stopProcessEvent)
        self.exitProgram = wx.Button(self, label='Exit')
        self.exitProgram.Bind(wx.EVT_BUTTON, self.exitProgramEvent)
        process_sizer.Add(self.startProcess, 0, wx.ALL|wx.CENTER, 5)
        process_sizer.Add(self.stopProcess, 0, wx.ALL|wx.CENTER, 5)
        process_sizer.Add(self.exitProgram, 0, wx.ALL|wx.CENTER, 5)

        self.progressBar = wx.Gauge(self, id=0, size=(400, 50), style=wx.GA_HORIZONTAL, range=100, name='Progress')
        progress_sizer.Add(self.progressBar, 1, wx.ALL|wx.EXPAND, 5)

        self.log_control = wx.TextCtrl(self, wx.NewId(), size=(4000,4000), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2|wx.TE_AUTO_URL|wx.TE_LEFT|wx.TE_BESTWRAP)
        Logging.SetGuiLogging(self.log_control)
        logger_sizer.Add(self.log_control, 1, wx.ALL|wx.EXPAND, 5)

        sizer.Add(process_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(progress_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(logger_sizer, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        # self.log_control.LoadFile(os.path.join(logfile_path, logfilename))


    def startProcessEvent(self, event):
        self.max_filenumber = 0
        self.current_filenumber = 0
        btn = event.GetEventObject().GetLabel()
        self.startProcess.Enable(False)
        self.stopProcess.Enable(True)
        self.progressBar.SetValue(1)
        logging.debug('Label of pressed button = {}'.format(btn))
        filelist = FileListWithProjection.FileListWithProjection()
        filelist.create_list('/common/las/', '/common/lasout/', 'WGS84geo', 'EOV2014fine')
        _thread.start_new_thread(self.longrunTransform, (), {'filelist':filelist.filelist})

    def longrunTransform(self, filelist):
        file_queue = filelist
        self.max_filenumber = len(file_queue)
        logging.debug(file_queue)
        results = []
        no_threads = False

        # If we got one file, start only one process
        cores = 2
        # Do not use threads when only use one core and disable threads
        # Probably this is related to https://github.com/grantbrown/laspy/issues/32
        if no_threads is True:
            logging.info('Do not use threads.')
            for lst in file_queue:
                TransformerWorkflow.Transformer(lst)
        # Generally we use this to process transfromration
        else:
            logging.info('Using threads on {0} cores.'.format(cores))
            pool = multiprocessing.Pool(processes=cores)
            for f in file_queue:
                results.append(pool.map_async(TransformerWorkflow.Transformer, (f,), callback=self.callbackTransformEvent))
            pool.close()
            pool.join()
        del file_queue
        self.progressBar.SetValue(100)
        logging.info('Finished, exiting and go home ...')
        self.startProcess.Enable(True)
        self.stopProcess.Enable(False)

    def callbackTransformEvent(self, filename):
        self.current_filenumber += 1
        pcnt = math.floor((self.current_filenumber + 1) / (self.max_filenumber + 1) * self.progressBar.GetRange())
        logging.info('{} file(s) of {} file(s) ({} %) already transformed'.format(self.current_filenumber, self.max_filenumber, pcnt))
        self.progressBar.SetValue(pcnt)

    def stopProcessEvent(self, event):
        btn = event.GetEventObject().GetLabel()
        logging.debug('Label of pressed button = {}'.format(btn))

    def exitProgramEvent(self,event):
        btn = event.GetEventObject().GetLabel()
        logging.debug('Label of pressed button = {}'.format(btn))
        logging.info ('You can not exit here!')


class HelloFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        try:
            os.mkdir(os.path.join(logfile_path))
        except FileExistsError:
            pass
        logging.info(script_header)

        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)
        icon_path = 'res/eagle_small.png'
        self.SetIcon(wx.Icon(icon_path))

        # create a panel in the frame
        self.pnl = wx.Panel(self)
        # Here we create a panel and a notebook on the panel
        self.nb = wx.Notebook(self.pnl)

        # create the page windows as children of the notebook
        self.pageFiles = PageFiles(self.nb)
        self.pageSettings = PageSettings(self.nb)
        self.pageProcess = PageProcess(self.nb)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.pageSettings, 'Settings')
        self.nb.AddPage(self.pageFiles, 'Files')
        self.nb.AddPage(self.pageProcess, 'Process')

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.pnl.SetSizer(sizer)

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
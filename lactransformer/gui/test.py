#!/bin/python

import datetime
import glob
import logging
import math
import multiprocessing
import os
import textwrap
import threading
from pathlib import Path

import wx

from lactransformer.libs import Logging, FileListWithProjection, TransformerWorkflow
from lactransformer.libs import supported_projections

SUPPORTED_FILETYPES = ('LAS Point Cloud files (*.las)|*.las|'
                       'TXT Point Cloud files (*.txt)|*.txt|'
                       'TerraPhoto Image list files (*.iml)|*.iml|'
                       'Riegl Camera CSV files (*.csv)|*.csv|'
                       'Riegl PEF files (*.pef)|*.pef')

app_name = 'LAC Transformer'
script_path = Path(__file__)

# Logging
logfile_path = script_path.parent.parent / 'log'
logfilename = f'lactransformer_{datetime.datetime.today().strftime("%Y%m%d_%H%M%S")}.log'
Logging.SetLogging(str(logfile_path / logfilename))

script_header = textwrap.dedent('''LAS & Co Transformer''')
__version__ = '0.0.0.6'


class PageFiles(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Filename')

        self.addFileButton = wx.Button(self, label='Add a file')
        self.addFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.addDirectoryButton = wx.Button(self, label='Add a Folder')
        self.addDirectoryButton.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        self.removeSelectedButton = wx.Button(self, label='Remove selected')
        self.removeSelectedButton.Enable(False)
        self.removeSelectedButton.Bind(wx.EVT_BUTTON, self.onRemoveSelected)
        self.removeAllButton = wx.Button(self, label='Remove all')
        self.removeAllButton.Enable(False)
        self.removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAll)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.addFileButton, 0, wx.ALL | wx.CENTER, 2)
        button_sizer.Add(self.addDirectoryButton, 0, wx.ALL | wx.CENTER, 2)
        button_sizer.Add(self.removeSelectedButton, 0, wx.ALL | wx.CENTER, 2)
        button_sizer.Add(self.removeAllButton, 0, wx.ALL | wx.CENTER, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 2)
        self.SetSizer(sizer)

    def onOpenFile(self, event):
        dlg = wx.FileDialog(self, 'Open a supported file', '', '',
                            SUPPORTED_FILETYPES, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.updateDisplay(dlg.GetPath())
        dlg.Destroy()

    def onOpenDirectory(self, event):
        dlg = wx.DirDialog(self, 'Open a directory with supported files', '',
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.updateDisplay(dlg.GetPath())
        dlg.Destroy()

    def updateDisplay(self, folder_path):
        paths = glob.glob(folder_path + '/*.*')
        for index, path in enumerate(paths):
            self.list_ctrl.InsertItem(index, os.path.basename(path))
        self.updateElemCountDependent()

    def onRemoveSelected(self, event):
        self.updateElemCountDependent()

    def onRemoveAll(self, event):
        self.list_ctrl.DeleteAllItems()
        self.updateElemCountDependent()

    def updateElemCountDependent(self):
        has_items = self.list_ctrl.GetItemCount() > 0
        self.removeSelectedButton.Enable(has_items)
        self.removeAllButton.Enable(has_items)


class PageSettings(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        projection_choices = sorted(set(supported_projections.projectionnames.values()))

        button_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Projection')
        button_sizer.Add(wx.StaticText(self, -1, 'Input projection'), 0, wx.ALL | wx.CENTER | wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.Choice(self, choices=projection_choices, name='Input projection'), 0, wx.ALL | wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.StaticText(self, -1, 'Output projection'), 0, wx.ALL | wx.CENTER | wx.ALIGN_LEFT, 5)
        button_sizer.Add(wx.Choice(self, choices=projection_choices, name='Output projection'), 0, wx.ALL | wx.ALIGN_LEFT, 5)

        process_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Process')
        process_sizer.Add(wx.StaticText(self, -1, 'Cores'), 0, wx.ALL | wx.CENTER, 5)
        process_number = wx.Slider(self, minValue=1, maxValue=16,
                                   style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS | wx.SL_BOTTOM,
                                   size=(200, 50), name='Cores')
        process_number.Bind(wx.EVT_SCROLL_CHANGED, self.sliderProcessEvent)
        process_sizer.Add(process_number, 0, wx.ALL | wx.EXPAND, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(process_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

    def sliderProcessEvent(self, event):
        value = event.GetEventObject().GetValue()
        logging.debug(f'Cores slider value: {value}')


class PageProcess(wx.Panel):
    def __init__(self, parent):
        self.max_filenumber = 0
        self.current_filenumber = 0
        super().__init__(parent)

        self.startProcess = wx.Button(self, label='Start process')
        self.startProcess.Bind(wx.EVT_BUTTON, self.startProcessEvent)
        self.stopProcess = wx.Button(self, label='Stop process')
        self.stopProcess.Enable(False)
        self.stopProcess.Bind(wx.EVT_BUTTON, self.stopProcessEvent)
        self.exitProgram = wx.Button(self, label='Exit')
        self.exitProgram.Bind(wx.EVT_BUTTON, self.exitProgramEvent)

        process_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Process control')
        process_sizer.Add(self.startProcess, 0, wx.ALL | wx.CENTER, 5)
        process_sizer.Add(self.stopProcess, 0, wx.ALL | wx.CENTER, 5)
        process_sizer.Add(self.exitProgram, 0, wx.ALL | wx.CENTER, 5)

        self.progressBar = wx.Gauge(self, id=0, size=(400, 50),
                                    style=wx.GA_HORIZONTAL, range=100, name='Progress')
        progress_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Progress')
        progress_sizer.Add(self.progressBar, 1, wx.ALL | wx.EXPAND, 5)

        self.log_control = wx.TextCtrl(self, wx.NewIdRef(), size=(4000, 4000),
                                       style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 |
                                             wx.TE_AUTO_URL | wx.TE_LEFT | wx.TE_BESTWRAP)
        Logging.SetGuiLogging(self.log_control)
        logger_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Console output')
        logger_sizer.Add(self.log_control, 1, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(process_sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(progress_sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(logger_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

    def startProcessEvent(self, event):
        self.max_filenumber = 0
        self.current_filenumber = 0
        self.startProcess.Enable(False)
        self.stopProcess.Enable(True)
        self.progressBar.SetValue(1)
        logging.debug(f'Start process: {event.GetEventObject().GetLabel()}')
        try:
            # NOTE: update these paths or make them configurable via PageFiles
            filelist = FileListWithProjection.FileListWithProjection()
            filelist.create_list('/common/las/', '/common/lasout/', 'WGS84geo', 'EOV2014fine')
            t = threading.Thread(target=self.longrunTransform, kwargs={'filelist': filelist.filelist}, daemon=True)
            t.start()
        except FileNotFoundError as err:
            logging.error(f'Cannot start processing: {err}')
            self.startProcess.Enable(True)
            self.stopProcess.Enable(False)

    def longrunTransform(self, filelist):
        file_queue = filelist
        self.max_filenumber = len(file_queue)
        logging.debug(file_queue)
        cores = 2
        logging.info(f'Using threads on {cores} cores.')
        pool = multiprocessing.Pool(processes=cores)
        for f in file_queue:
            pool.map_async(TransformerWorkflow.Transformer, (f,), callback=self.callbackTransformEvent)
        pool.close()
        pool.join()
        del file_queue
        self.progressBar.SetValue(100)
        logging.info('Finished, exiting and go home ...')
        self.startProcess.Enable(True)
        self.stopProcess.Enable(False)

    def callbackTransformEvent(self, filename):
        self.current_filenumber += 1
        pcnt = math.floor(
            (self.current_filenumber + 1) / (self.max_filenumber + 1) * self.progressBar.GetRange())
        logging.info(
            f'{self.current_filenumber} file(s) of {self.max_filenumber} file(s) ({pcnt}%) already transformed')
        self.progressBar.SetValue(pcnt)

    def stopProcessEvent(self, event):
        logging.debug(f'Stop process: {event.GetEventObject().GetLabel()}')

    def exitProgramEvent(self, event):
        logging.debug(f'Exit: {event.GetEventObject().GetLabel()}')
        logging.info('You can not exit here!')


class HelloFrame(wx.Frame):
    def __init__(self, *args, **kw):
        logfile_path.mkdir(parents=True, exist_ok=True)
        logging.info(script_header)

        super().__init__(*args, **kw)
        icon_path = 'res/eagle_small.png'
        self.SetIcon(wx.Icon(icon_path))

        self.pnl = wx.Panel(self)
        self.nb = wx.Notebook(self.pnl)

        self.pageFiles = PageFiles(self.nb)
        self.pageSettings = PageSettings(self.nb)
        self.pageProcess = PageProcess(self.nb)

        self.nb.AddPage(self.pageSettings, 'Settings')
        self.nb.AddPage(self.pageFiles, 'Files')
        self.nb.AddPage(self.pageProcess, 'Process')

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.pnl.SetSizer(sizer)

        self.makeMenuBar()
        self.CreateStatusBar()
        self.SetStatusText(f'Welcome to the {app_name} application!')

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        helloItem = fileMenu.Append(-1, '&Hello...\tCtrl-H',
                                    'Help string shown in status bar for this menu item')
        fileMenu.AppendSeparator()
        openfileItem = fileMenu.Append(-1, '&Open file...\tCtrl-O', 'Open a supported file')
        opendirectoryItem = fileMenu.Append(-1, 'Open &directory...\tCtrl-Shift-O',
                                            'Open a directory with supported files')
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, '&File')
        menuBar.Append(helpMenu, '&Help')
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnOpenFile, openfileItem)
        self.Bind(wx.EVT_MENU, self.OnOpenDirectory, opendirectoryItem)
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close(True)

    def OnOpenFile(self, event):
        dlg = wx.FileDialog(self, 'Open a supported file', '', '',
                            SUPPORTED_FILETYPES, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            logging.info(f'Selected file: {dlg.GetPath()}')
        dlg.Destroy()

    def OnOpenDirectory(self, event):
        dlg = wx.DirDialog(self, 'Open a directory with supported files', '',
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.pageFiles.updateDisplay(dlg.GetPath())
        dlg.Destroy()

    def OnHello(self, event):
        wx.MessageBox('Hello again from wxPython')

    def OnAbout(self, event):
        wx.MessageBox(
            'This is a wxPython based GUI for LAC Transformer. '
            'It transforms LAS and TXT Point Clouds, Riegl CSV and PEF files between supported projections.',
            f'About {app_name}',
            wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wx.App()
    frm = HelloFrame(None, title='LAC Transformer')
    frm.Show()
    app.MainLoop()

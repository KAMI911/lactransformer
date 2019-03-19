try:
    import traceback
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)

class WxTextCtrlHandler(logging.Handler):

    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        import wx
        wx.CallAfter(self.ctrl.WriteText, s)


def SetLogging(logfilename):
    # set up logging to file - see previous section for more details
    logging.basicConfig(
        filename=logfilename,
        filemode='w',
        format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y.%m.%d. %H:%M:%S',
        level=logging.DEBUG)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d. %H:%M:%S')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

def SetGuiLogging(gui_log_control):
    gui_logger = WxTextCtrlHandler(gui_log_control)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d. %H:%M:%S')
    gui_logger.setFormatter(formatter)
    logging.getLogger('').addHandler(gui_logger)

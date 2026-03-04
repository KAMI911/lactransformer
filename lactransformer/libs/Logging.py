try:
    import traceback
    import logging
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


class WxTextCtrlHandler(logging.Handler):

    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl

    def emit(self, record):
        import wx
        wx.CallAfter(self.ctrl.WriteText, self.format(record) + '\n')


def SetLogging(logfilename):
    logging.basicConfig(
        filename=logfilename,
        filemode='w',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y.%m.%d. %H:%M:%S',
        level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d. %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def SetGuiLogging(gui_log_control):
    gui_logger = WxTextCtrlHandler(gui_log_control)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d. %H:%M:%S')
    gui_logger.setFormatter(formatter)
    logging.getLogger('').addHandler(gui_logger)

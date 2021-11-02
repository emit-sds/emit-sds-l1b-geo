import logging

logger = logging.getLogger('emit')

class L1bGeoLogFormatter(logging.Formatter):
    '''Set logging format, optionally with color'''
    def __init__(self, add_color = True):
        self.add_color = add_color

    def color_text(self, text, levelno):
        # ANSI colors
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        if(not self.add_color):
            return text
        if(levelno == logging.DEBUG):
            return OKBLUE + text + ENDC
        elif(levelno == logging.INFO):
            return OKGREEN + text + ENDC
        elif(levelno == logging.WARNING):
            return WARNING + text + ENDC
        elif(levelno == logging.ERROR):
            return FAIL + text + ENDC
        elif(levelno == logging.CRITICAL):
            return FAIL + text + ENDC
        return text
    def format(self, record):
        return (self.color_text(record.levelname + ": ", record.levelno) +
                record.getMessage())
        

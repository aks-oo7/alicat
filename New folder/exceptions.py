# from helpers.config import ROOT_URL
import logging
import sys, os
import traceback
import datetime
import requests
import urllib3
import json

# Disable false CA warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'current_domain.json'), 'r') as config:
    f = config.read()
    DOMAIN = json.loads(f)['current']

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.json'), 'r') as config:
    f = config.read()
    data = json.loads(f)[DOMAIN]
    ROOT_URL = json.loads(f)[DOMAIN]['rootURL']


class GeminiException(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        msg = self.msg
        
        if 'Bin' in msg: return msg # Added for pilot 4/20/23 - RC
        if msg:
            return """

        Gemini Error
* * * * * * * * * * * * * * *
- ERROR -  {}
* * * * * * * * * * * * * * *
            """.format(msg)
        else:
            return ""


class TestCaseCanceled(GeminiException):
    pass


class TestCaseFailed(GeminiException):
    pass


class RegressionFailed(GeminiException):
    pass


class UnknownHeaterType(GeminiException):
    pass


class HeaterOverTemp(GeminiException):
    pass


class DidNotMeetSpec(GeminiException):
    pass


class StandardSpecNotFound(GeminiException):
    pass


class FailedToFind(GeminiException):
    pass


class TableConfigurationFailed(GeminiException):
    pass


class KeyPNSyntaxError(GeminiException):
    pass


class ExceptLogger():
    def __init__(self, ttvid):
        self.ttvid = ttvid
        sys.excepthook = self.log_exception

    def log_exception(self, exctype, value, tb):
        format_exception = [line.rstrip('\n') for line in traceback.format_exception(exctype, value, tb)]
        text_for_api = self.write_error_to_logfile(format_exception)
        # send error traceback to API
        self.log_script_error(text_for_api, tb.tb_lineno, exctype)
        
    def write_error_to_logfile(self, format_exception):
        text_for_api = ''
        # Create directories in the path if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs',
                               'ExceptionLog_{}_{}.log'.format(self.ttvid, datetime.datetime.now().strftime("%m%d%Y"))),
                  'a') as file:
            dt = datetime.datetime.now().strftime("%H:%M:%S")
            file.write('\n')
            for i in format_exception:
                line_text = '[{}] {}\n'.format(dt, i.replace('\n', '\n[{}]'.format(dt)).replace('\t', '').lstrip())
                text_for_api += line_text
                file.write(line_text)
            file.write('\n')
            print(text_for_api)
        return text_for_api
    
    def log_script_error(self, text_for_api, line, exctype):
        requests.post('{}://{}/api/script_error_logging/'.format(data['scheme'], ROOT_URL),
                          data={'text': text_for_api, 'testTableVersionId': self.ttvid, 'type': exctype.__name__,
                                'line': line}, verify=False)


class CancelError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'CancelError: {}'.format(self.message)
        return 'CancelError has been raised'
    
class AbortedError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'AbortedError: {}'.format(self.message)
        return 'Execution aborted due to error'
    
class ConnectionClosedError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ConnectionClosedError: {}'.format(self.message)
        return 'Execution aborted due to ConnectionClosedError'


if __name__ == '__main__':
    print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'))
    print(DOMAIN)
    print(ROOT_URL)
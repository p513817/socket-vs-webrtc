# Basic
import cv2, time, logging, base64, threading, os, sys, copy, json, colorlog, socket
import traceback

from flask import abort, request
from werkzeug.utils import secure_filename

import inspect, ctypes

# Define Variable
LOG_LEVEL = {   
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR  
}

def config_logger(log_name=None, write_mode='a', level='Debug', clear_log=False):

    logger = logging.getLogger()            # get logger
    logger.setLevel(LOG_LEVEL[level.lower()])       # set level
    
    if not logger.hasHandlers():    # if the logger is not setup
        basic_formatter = logging.Formatter( "%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)", "%y-%m-%d %H:%M:%S")
        formatter = colorlog.ColoredFormatter( "%(asctime)s %(log_color)s [%(levelname)-.4s] %(reset)s %(message)s %(purple)s (%(filename)s:%(lineno)s)", "%y-%m-%d %H:%M:%S")
        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOG_LEVEL[level.lower()])
        logger.addHandler(stream_handler)

        # add file handler
        if clear_log and os.path.exists(log_name):
            logging.warning('Clearing exist log files')
            os.remove(log_name)
            
        if log_name:
            file_handler = logging.FileHandler(log_name, write_mode, 'utf-8')
            file_handler.setFormatter(basic_formatter)
            file_handler.setLevel(LOG_LEVEL['info'])
            logger.addHandler(file_handler)
    
        logger.info('Create logger.({})'.format(logger.name))
        logger.info('Enabled stream {}'.format(f'and file mode.({log_name})' if log_name else 'mode'))
    return logger

# Utilties
def get_address():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def get_cam(input):
    cap = cv2.VideoCapture(input)
    cap.set(6, cv2.VideoWriter.fourcc('M','J','P','G'))
    cap.set(4, 1080)
    cap.set(3, 1920)
    return cap

# Stop Thread
def _async_raise(tid, exctype):
    # raises the exception, performs cleanup if needed
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def handle_exception(error, title="Error", exit=False):
    
    # Get Error Class ( type )
    error_class = error.__class__.__name__ 
    
    # Get Detail
    detail = error.args[0] 

    # Get Call Stack
    cl, exc, tb = sys.exc_info() 

    # Last Data of Call Stack
    last_call_stack = traceback.extract_tb(tb)[-1] 

    # Parse Call Stack and Combine Error Message
    file_name = last_call_stack[0] 
    line_num = last_call_stack[1] 
    func_name = last_call_stack[2] 
    err_msg = "{} \nFile \"{}\", line {}, in {}: [{}] {}".format(title, file_name, line_num, func_name, error_class, detail)
    
    logging.error(err_msg)
    if exit: sys.exit()

    return err_msg
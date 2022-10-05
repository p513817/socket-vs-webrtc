import cv2, time, logging, os, sys
import threading

# from eventlet.green import threading
# import eventlet
# eventlet.monkey_patch()

def check_file_exist(path):
    return True if os.path.exists(path) else False
        
class Img:
    def __init__(self, input_data) -> None:
        self.img = cv2.imread(input_data)

    def release(self):
        self.img=None

    def __del__(self):
        self.img=None

    def read(self):
        # if not None then return true
        return (self.img is not None), self.img

class Source():
    
    def __init__(self, input_data, intype):

        self.src = None
        self.ret, self.frame = None, None
        self.first_frame, self.first_frame_ready = None, False
        
        self.input_data = input_data.rstrip().replace('\n', '').replace(' ', '')
        self.intype = intype
        self.status, self.err = self.check_status()
        logging.warning('Detect source type is : {}'.format(self.intype))
        
        if self.status:
            if intype in ['V4L2', 'Video']:
                self.src = cv2.VideoCapture(self.input_data)

                self.src.set(6, cv2.VideoWriter.fourcc('M','J','P','G'))
                self.src.set(4, 1080)
                self.src.set(3, 1920)

            elif intype=='Image':
                self.src = Img(self.input_data)            
            elif intype=='RTSP':
                self.src = cv2.VideoCapture(self.input_data)
            else:
                logging.error('Unexcepted input data.')

        self.ret, self.frame = self.src.read()

        self.start_time = time.time() 
        self.stop_time  = self.start_time + 5
        self.isStop = False
        self.t = threading.Thread( target = self.update )
        logging.info("Init Source Object ... Finished ! ")

        self.frame_idx = 0

    def __del__(self):
        self.stop()
        
    def check_status(self):
        status, err_msg = True, ""
        if self.intype in ['Video', 'Image', 'V4L2']:
            # check file exist
            if not os.path.exists(self.input_data):
                status = False
                err_msg = "Could not find data ({})".format(self.input_data)

        return status, err_msg

    def get_status(self):            
        return self.status, self.err

    def get_type(self):
        return self.intype

    def update(self):
        """
        Threading Part
        """
        while(True):
            self.frame_idx += 1
            # logging.debug(f"{self.frame_idx}")
            if(self.isStop): break
            self.ret, self.frame = self.src.read()
            
            # self.show_cv_win()
                    
        self.release()

    def get_index(self):
        return self.frame_idx

    def get_thread_indent(self):
        return self.t.ident

    def get_addr(self):
        return id(self.src)

    def show_cv_win(self):
        cv2.imshow("TEST", self.frame)
        if (cv2.waitKey(1) in [ ord('q'), ord('Q'), 27 ] ):
            cv2.destroyAllWindows()
            return False
        return True

    def start(self):
        logging.info("Start Stream ... ")
        self.t.start()
        logging.info("Start Stream ... Done ")
        return self.t

    def stop(self):
        self.isStop = True
        self.t.join()

    def release(self):
        try:
            self.stop()
            self.src.release()
        except:
            logging.warning('Could not release object')
        finally:
            logging.warning('Set source to `None`')
            self.src=None
    
    def read(self):
        return self.ret, self.frame.copy()
    
    def get_shape(self):
        w, h = self.src.get(cv2.CAP_PROP_FRAME_WIDTH), self.src.get(cv2.CAP_PROP_FRAME_HEIGHT)  
        logging.debug("The source width: {}, height: {}".format(w, h))
        return ( int(w), int(h) )


# class Source():
    
#     def __init__(self, input_data, intype):

#         self.src = None
#         self.ret, self.frame = None, None
#         self.first_frame, self.first_frame_ready = None, False
        
#         self.input_data = input_data.rstrip().replace('\n', '').replace(' ', '')
#         self.intype = intype
#         self.status, self.err = self.check_status()
#         logging.warning('Detect source type is : {}'.format(self.intype))
        
#         if self.status:
#             if intype in ['V4L2', 'Video']:
#                 self.src = cv2.VideoCapture(self.input_data)
#             elif intype=='Image':
#                 self.src = Img(self.input_data)            
#             elif intype=='RTSP':
#                 self.src = cv2.VideoCapture(self.input_data)
#             else:
#                 logging.error('Unexcepted input data.')

#         self.ret, self.frame = self.src.read()

#         self.start_time = time.time() 
#         self.stop_time  = self.start_time + 5
#         self.isStop = False
#         self.t = threading.Thread( target = self.update )
#         logging.info("Init Source Object ... Finished ! ")

#         self.frame_idx = 0

#     def __del__(self):
#         self.stop()
        
#     def check_status(self):
#         status, err_msg = True, ""
#         if self.intype in ['Video', 'Image', 'V4L2']:
#             # check file exist
#             if not os.path.exists(self.input_data):
#                 status = False
#                 err_msg = "Could not find data ({})".format(self.input_data)

#         return status, err_msg

#     def get_status(self):            
#         return self.status, self.err

#     def get_type(self):
#         return self.intype

#     def update(self):
#         """
#         Threading Part
#         """
#         while(True):
#             self.frame_idx += 1
#             # logging.debug(f"{self.frame_idx}")
#             if(self.isStop): break
#             self.ret, self.frame = self.src.read()
#             # self.show_cv_win()
                

#         self.release()

#     def get_index(self):
#         return self.frame_idx

#     def get_thread_indent(self):
#         return self.t.ident

#     def get_addr(self):
#         return id(self.src)

#     def show_cv_win(self):
#         cv2.imshow("TEST", self.frame)
#         if (cv2.waitKey(1) in [ ord('q'), ord('Q'), 27 ] ):
#             cv2.destroyAllWindows()
#             return False
#         return True

#     def start(self):
#         logging.info("Start Stream ... ")
#         self.t.start()
#         logging.info("Start Stream ... Done ")
#         return self.t

#     def stop(self):
#         self.isStop = True
#         self.t.join()

#     def release(self):
#         try:
#             self.stop()
#             self.src.release()
#         except:
#             logging.warning('Could not release object')
#         finally:
#             logging.warning('Set source to `None`')
#             self.src=None
    
#     def read(self):
#         return self.ret, self.frame.copy()
    
#     def get_shape(self):
#         w, h = self.src.get(cv2.CAP_PROP_FRAME_WIDTH), self.src.get(cv2.CAP_PROP_FRAME_HEIGHT)  
#         logging.debug("The source width: {}, height: {}".format(w, h))
#         return ( int(w), int(h) )


if __name__ == "__main__":
    from utils import config_logger
    config_logger()
    logging.info('Testing source.py')

    src = Source("/dev/video0", 'V4L2')
    src.start()

    while(True):
        ret, frame = src.read()

        cv2.imshow('Test', frame)
        if cv2.waitKey(200)==ord('q'):
            break
    
    src.release()
# Import Python Module

# Basic
import os, sys, json, logging, cv2, base64, signal, copy, time, threading
import subprocess as sb

# Flask
from flask import Flask, Blueprint, jsonify, render_template
from flask_cors import CORS as cors
from flask_sock import Sock

# Gst
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer,GObject


# Custom
this_path = os.path.dirname( os.path.realpath(__file__))
sys.path.append(this_path)
from utils import get_address, config_logger, get_cam, stop_thread
from source import Source
from def_gst_rtsp import SensorFactory, GstServer, GstLoop

# --------------------------------------
# Parameter Define

# Const
# DEVICE      = 0
INPUT      = '/dev/video0'
INPUT_TYPE  = 'V4L2'

PORT        = 4444
DEBUG       = False

BASE64_DEC  = "utf-8"
BASE64_EXT  = '.jpg'

NAMESPACE   = '/stream'
IMG_EVENT   = 'images'
SOURCE      = 'source'

STREAM      = 'STREAM'
IS_STREAM   = 'IS_STREAM'
SEND_SOCKET = 'SEND_SOCKET'
RTSP        = "RTSP"
SRC         = "SRC"
GMAIN       = "GMAIN"
TASK        = "TASK"
FRAME       = "FRAME"

temp_frame = None

# --------------------------------------
# Define Basic Function
def create_app():
    # init logger
    config_logger(log_name="stream-cmp.log")
    
    # initialize flask
    app = Flask(__name__)

    # update configuration
    app.config.update(
        HOST            = get_address(),
        PORT            = PORT,
        DEBUG           = DEBUG,
        STREAM          = None,
        IS_STREAM       = False,
        SEND_SOCKET     = False,
        USB_RELOADER    = False,
        RTSP            = None,
        SRC             = None,
        GMAIN           = None,
        TASK            = {}
    )
    # share resource
    cors(app)                                                       

    # Define Socket
    sock = Sock(app)

    # Define Streamer

    logging.info("Init Camera Stream ... ")
    app.config[SRC] = Source(INPUT, INPUT_TYPE)
    app.config[SRC].start()
    logging.info("Init Camera Stream ... PASS")

    logging.info("Init GstServer ... ")
    RtspServer=GstServer(app.config[SRC])
    logging.info("Init GstServer ... PASS")

    logging.info("Init GstLoop ... ")
    app.config[GMAIN] = GstLoop()
    app.config[RTSP] = threading.Thread(
        target = app.config[GMAIN].start
    )
    app.config[RTSP].daemon = True
    logging.info("Init GstLoop ... PASS")

    logging.info("Start GstLoop ... ")
    app.config[RTSP].start()
    logging.info("Start GstLoop ... PASS")

    # End Define Streamer

    # --------------------------------------
    # Register Route

    @sock.route('/echo')
    def echo(sock):
        while True:
            data = sock.receive()
            logging.info(data)
            sock.send(data)

    @sock.route('/stream')
    def stream(sock):
        while True:
            
            resp = ' { "images": "" } '

            logging.info("="*20)
            t1 = time.time()
            data = sock.receive()
            t2 = time.time()
            
            logging.info("Receive Time: {}".format(round(t2-t1, 4)))
            
            task = json.loads(data)["task"].strip()

            if not (task in app.config.keys()): 
                logging.warning("No such Task {}".format(task))
                continue

            t3 = time.time()
            if (FRAME in app.config[TASK]):
                resp = json.dumps( {"images": app.config[TASK][FRAME] } )
            t4 = time.time()

            logging.info("JSON Parse Time: {}".format(round(t4-t3, 4)))
            sock.send(resp)
            t5 = time.time()

            logging.info("Send Time: {}".format(round(t5-t4, 4)))

            logging.info("Cost Time: {}".format(round(t5-t1, 4)))
            # else:
            #     print('No Frame ... ', end="")

            # sock.send(json.dumps( {"images": task } ))

    @app.route("/", methods=['GET', 'POST'])
    def index():
        return render_template("index.html")

    @app.route("/socket/start/", methods=["GET"])
    def socket_start():

        if( app.config[STREAM] == None):
            logging.debug("Create Socket Thread ! ")
            app.config[STREAM] = threading.Thread(
                target = socket_stream_task,
                args = ( app.config[SRC], ) 
            )
            app.config[STREAM].daemon = True
        
        if( not app.config[STREAM].is_alive()):
            logging.debug("Start Socket Thread ! ")
            app.config[IS_STREAM] = True
            app.config[STREAM].start()


        msg = "Started Socket Stream ! ( Space:{}, Event:{} )".format( NAMESPACE, IMG_EVENT )
        logging.info( msg )
        return jsonify(msg), 200


    @app.route("/socket/stop/", methods=["GET"])
    def socket_stop():
        app.config[IS_STREAM] = False
        app.config[STREAM].join()
        app.config[STREAM] = None

        msg = "Stop Socket Stream"
        logging.info( msg )
        return jsonify(msg), 200

    @app.route("/rtsp/start/", methods=["GET"])
    def rtsp_start():
        msg = "Started RTSP Stream"
        logging.info( msg )
        return jsonify(msg), 200

    @app.route("/rtsp/stop/", methods=["GET"])
    def rtsp_stop():
        msg = "Stoped RTSP Stream"
        logging.info( msg )
        return jsonify(msg), 200

    return app, sock

# AI Task
def socket_stream_task(src):
    
    global temp_frame

    while(True):

        if( not app.config[IS_STREAM]): break

        # Get the frame from source
        ret, frame = app.config[SRC].read()
        
        if(not ret): 
            logging.debug("Wait frame ...")
            continue

        # Convert to base64 format
        frame_base64 = base64.encodebytes(cv2.imencode(BASE64_EXT, frame)[1].tobytes()).decode(BASE64_DEC)
        
        # Send socketio to client
        if not (FRAME in app.config[TASK]): 
            app.config[TASK].update( {FRAME: []} )

        app.config[TASK][FRAME] = frame_base64

        time.sleep(1/5)
        
    logging.info('Stop streaming')

def get_stream_thread(src, func):
    t = threading.Thread(
            target=func, 
            args=( src, ))
    t.daemon = True
    return t

if __name__ == "__main__":
    app, sock = create_app()
    
    app.run(
        "0.0.0.0", 4444
    )

    """

    python3 ./3/app.py

    """

else:
    # For Gunicorn
    app, sock = create_app()

    """

    cd 3 && \
    gunicorn \
    -c _gunicorn.conf.py \
    --workers 1 \
    --worker-class eventlet \
    --bind 0.0.0.0:4444 \
    app:app

    """
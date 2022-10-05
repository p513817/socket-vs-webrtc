# Import Python Module

# Basic
import os, sys, json, logging, cv2, base64, signal, copy, time, threading
import subprocess as sb

# Flask
from flask import Flask, Blueprint, jsonify, render_template
from flask_cors import CORS as cors
from flask_sock import Sock

# Custom Module
sys.path.append(os.path.dirname( os.path.realpath(__file__)))
from utils.utils import get_address, config_logger
from utils.source import Source
from utils.def_gst_rtsp import GstServer, GstLoop

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

    # Launch Camera Capture Thread
    app.config[SRC] = Source(INPUT, INPUT_TYPE)
    app.config[SRC].start()
    logging.info("Init Camera Stream ... PASS")

    # Define GstServer
    RtspServer=GstServer(app.config[SRC])
    logging.info("Init GstServer ... PASS")

    # Create GstLoop Object and start it
    app.config[GMAIN] = GstLoop()
    app.config[RTSP] = threading.Thread( target = app.config[GMAIN].start )
    app.config[RTSP].daemon = True
    app.config[RTSP].start()
    logging.info("Start GstLoop ... PASS")

    # --------------------------------------
    # Register Route
    
    @sock.route('/stream')
    def stream(sock):
        while True:
            
            resp = ' { "images": "" } '

            data = sock.receive()
            
            task = json.loads(data)["task"].strip()

            if not (task in app.config.keys()): 
                logging.warning("No such Task {}".format(task))
                continue

            if (FRAME in app.config[TASK]):
                resp = json.dumps( {"images": app.config[TASK][FRAME] } )

            sock.send(resp)

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

def socket_stream_task(src):

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

# Run with Python
if __name__ == "__main__":
    app, sock = create_app()
    app.run( "0.0.0.0", 4444 )

# Run with Gunicorn
else:
    app, sock = create_app()
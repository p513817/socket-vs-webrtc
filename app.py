# Import Python Module

# Basic
from distutils.command.config import config
from distutils.log import log
import os, sys, json, logging, cv2, base64, signal, copy, time, threading
import subprocess as sb

# Flask
from flask import Flask, Blueprint, jsonify, render_template, abort, request
from flask_cors import CORS as cors
from flask_sock import Sock
from werkzeug.utils import secure_filename

# Custom Module
sys.path.append(os.path.dirname( os.path.realpath(__file__)))
from utils.utils import get_address, config_logger, handle_exception
from utils.source import Source
from utils.rtsp_server import GstServer, GstLoop

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

RTSP_SERVER = "RTSP_SERVER"

VID_EXT     = [ "mp4", "mkv", "avi" ]
IMG_EXT     = [ "jpg", "png", "bmp" ]

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
    
    # Define GstServer
    app.config[RTSP_SERVER] = GstServer()
    logging.info("Init GstServer ... PASS")

    # Define Source
    app.config[SRC] = dict()

    # # Source - 1 - Run Camera
    # streamID = "cam"
    # app.config[SRC][streamID] = Source(INPUT, INPUT_TYPE)
    # app.config[SRC][streamID].start()

    # # Add Source
    # app.config[RTSP_SERVER].add_source(
    #     src = app.config[SRC][streamID],
    #     uri = "/" + streamID
    # )

    # # Source - 2
    # streamID = "car"
    # app.config[SRC][streamID] = Source('./data/car.mp4', 'Video')
    # app.config[SRC][streamID].start()

    # # Add Source
    # app.config[RTSP_SERVER].add_source(
    #     src = app.config[SRC][streamID],
    #     uri = "/" + streamID
    # )

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

    @app.route("/get_v4l2/", methods=['GET'])
    def get_v4l2():
        import subprocess as sp
        ret_status, ret_message = 200, []

        # Get V4L2 Camera
        command = sp.run("ls /dev/video*", shell=True, stdout=sp.PIPE, encoding='utf8')
        
        # 0 means success
        if command.returncode == 0:

            # Parse Each Camera to a list
            ret_message = command.stdout.strip().split('\n')
            logging.debug("{}, {}".format(ret_message, type(ret_message)))
            
            # Check is failed_key in that information
            for msg in ret_message.copy():
                if int(msg.split("video")[-1])%2==1:
                    # if N is even it's not available for opencv
                    ret_message.remove(msg)
        
        # else not success
        else:
            ret_status  = 400
            ret_message = "Camera not found"

        return jsonify(ret_message), ret_status

    @app.route("/src/add", methods=["POST"])
    def create_source():
        """
        Create Source ...
        data: {
            "name"      : "test",
            "type"      : "v4l2",
            "source"    : "/dev/video0"
        }

        data: {
            "name"      : "test",
            "type"      : "video",
            "source"    : "file-path"
        }
        """
        ret_msg, ret_code = "Create Source Done !!! ", 200

        # Get data
        data = dict(request.form) if bool(request.form) else request.get_json()

        # if file
        if bool(request.files):
            file        = request.files["source"]
            file_name   = secure_filename(file.filename)
            file_path   = os.path.join( "./data", file_name )
            file.save( file_path )
            data["source"] = file_path
            logging.info("Detected file in add request, saved in {}".format(file_path))

            ext = os.path.splitext(file_name)[1].replace(".", "")
            if (ext in VID_EXT): data["type"]   = "Video"
            elif (ext in IMG_EXT): data["type"] = "Image"
            elif ext=="": raise Exception("Unknown data type ... {}".format(ext))
            else: raise Exception("Unknown data type ... {}".format(ext))
    
        # Create Source
        streamID = data["name"]
        app.config[SRC].update( {streamID: dict()} )

        try:
            app.config[SRC][streamID] = Source(data["source"], data["type"])
        except Exception as e:
            ret_msg, ret_code = "Create Source Error ... {}".format(handle_exception(e)), 200
            logging.error(ret_msg)
        
        return jsonify( ret_msg ), ret_code

    @app.route("/src/<streamID>/start/", methods=['GET'])
    def start_source(streamID):
        ret_stat, ret_msg = 400, ""

        try:
            app.config[SRC][streamID].start()
        except:
            ret_msg     = "Start Source Error"

        # Add Source
        try:
            app.config[RTSP_SERVER].add_source( src = app.config[SRC][streamID],
                                                uri = "/" + streamID )
            ret_msg = { "id"    : streamID,
                        "url"   : "http://127.0.0.1:8999/{}".format(streamID) }
        except Exception as e:
            ret_msg     = "Add Gstreamer Source Error ... {}".format(handle_exception(e))

        ret_stat = 200
        return jsonify( ret_msg ), ret_stat

    @app.route("/src/<streamID>/stop/", methods=['GET'])
    def stop_source(streamID):
        ret_code, ret_msg = 200, "Stopped Source"
        try:
            try:
                logging.info("Stopped Socket Stream")
                socket_stop()
            except Exception as e: pass

            app.config[SRC][streamID].release()
            logging.info("Stopped Source Thread")
        except Exception as e:
            ret_code, ret_msg = 400, "Stopped Source Error {}".format(handle_exception(e))
            logging.error(ret_msg)

        return jsonify(ret_msg), ret_code

    @app.route("/sources/", methods=["GET"])
    def source_list():
        src_list = list(app.config[SRC].keys())
        logging.info(src_list)
        return jsonify( src_list ), 200

    @app.route("/socket/start/", methods=["GET"])
    def socket_start():

        if( app.config[STREAM] == None):
            logging.debug("Create Socket Thread ! ")
            app.config[STREAM] = threading.Thread(
                target = socket_stream_task,
                args = ( app.config[SRC+"2"], ) 
            )
            app.config[STREAM].daemon = True
        
        if( not app.config[STREAM].is_alive()):
            logging.debug("Start Socket Thread ! ")
            app.config[IS_STREAM] = True
            app.config[STREAM].start()

        msg = "Started Socket Stream ! ( Space:{}, Event:{} )".format( NAMESPACE, IMG_EVENT )
        logging.info( msg )
        return jsonify(msg), 200

    @app.route("/socket/<streamID>/start/", methods=["GET"])
    def trg_socket_start(streamID):

        if( app.config[STREAM] == None):
            logging.debug("Create Socket Thread ! ")
            app.config[STREAM] = threading.Thread(
                target = socket_stream_task,
                args = ( app.config[SRC][streamID], ) 
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

        # Run Camera
        # app.config[SRC] = Source(INPUT, INPUT_TYPE)
        # app.config[SRC].start()

        # # Add Source
        # full_url = app.config[RTSP_SERVER].add_source(
        #     src = app.config[SRC],
        #     uri = "/test"
        # )

        return jsonify(full_url), 200

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
        ret, frame = src.read()
        
        if(not ret): 
            logging.debug("Wait frame ...")
            continue

        # Convert to base64 format
        frame_base64 = base64.encodebytes(cv2.imencode(BASE64_EXT, frame)[1].tobytes()).decode(BASE64_DEC)
        
        # Send socketio to client
        if not (FRAME in app.config[TASK]): 
            app.config[TASK].update( {FRAME: []} )

        app.config[TASK][FRAME] = frame_base64
        
    logging.info('Stop streaming')

# Run with Python
if __name__ == "__main__":
    app, sock = create_app()
    app.run( "0.0.0.0", 4444 )

# Run with Gunicorn
else:
    app, sock = create_app()
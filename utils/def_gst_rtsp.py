# Gstreamer
import gi, logging
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer, GObject

# Gstreamer RTSP Server and Media Factory#
# RTSP base on Gstreamer
# Define Factory
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    
    def __init__(self, cam):
        # Inherit Media Factory
        GstRtspServer.RTSPMediaFactory.__init__(self)

        self.cam = cam
        self.ret, self.frame = self.get_first_frame(self.cam)

        self.height, self.width = self.frame.shape[:2]
        self.fps = 30
        self.duration = 1 / self.fps * Gst.SECOND
        self.launch_string = \
        'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
        'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
        '! videoconvert ! video/x-raw,format=I420 ' \
        '! x264enc bitrate=2048 speed-preset=0 key-int-max=15 ' \
        '! video/x-h264,profile=baseline ' \
        '! rtph264pay name=pay0 pt=96'.format(
            self.width, self.height, self.fps )
    
    def on_need_data(self, src, lenght):
        ret, frame = self.cam.read()
        if ret:
            data = frame.tobytes()
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
            buf.duration = self.duration
            timestamp = self.number_frames * self.duration
            buf.pts = buf.dts = int(timestamp)
            buf.offset = timestamp
            self.number_frames += 1
            retval = src.emit('push-buffer', buf)
            if retval != Gst.FlowReturn.OK:
                print(retval)

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)
        
    def get_first_frame( self,  cam ):
        logging.info('Waiting for first frame ...')
        while(True):
            ret, frame = cam.read()
            if(ret): break
        logging.info('Captured the first frame')
        return ret, frame

class GstServer():
    """
    Define Gstreamer Server
    """
    def __init__(self, cam):
        # New RTSP Server
        self.server=GstRtspServer.RTSPOnvifServer.new()
        
        self.port="8999"
        self.server.set_service(self.port)
        self.server.connect("client-connected",self.client_connected)
        self.server.attach(None)
        factory = SensorFactory(cam)
        factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", factory)
        #  start serving
        print ("stream ready at rtsp://127.0.0.1:" + self.port + "/test")
        #  this com IP address
        print ("stream ready at rtsp://192.168.1.157:" + self.port+ "/test")
    
    def client_connected(self, arg1, arg2):      
        print('Client connected')

class GstLoop():
    def __init__ (self):
        Gst.init(None)
        self.loop = GLib.MainLoop()

    def start(self):
        logging.warning("Start GstLoop")
        self.loop.run()

    def stop(self):
        logging.warning("Stop GstLoop")
        self.loop.quit()
    

"""
gst-launch-1.0 v4l2src device=/dev/video0 \
! video/x-raw, width=1920, height=1080,framerate=30/1 \
! videoconvert ! fpsdisplaysink video-sink="autovideosink" sync=false fullscreen-overlay=true

gst-launch-1.0 v4l2src device=/dev/video0 \
! image/jpeg, width=1920, height=1080,framerate=30/1 \
! jpegparse ! jpegdec ! fpsdisplaysink video-sink="autovideosink" sync=false fullscreen-overlay=true

gst-launch-1.0 \
v4l2src device=/dev/video0 \
! image/jpeg, width=1920, height=1080,framerate=30/1 \
! jpegparse ! jpegdec ! fpsdisplaysink video-sink="autovideosink" sync=false fullscreen-overlay=true \
v4l2src device=/dev/video2 \
! image/jpeg, width=1920, height=1080,framerate=30/1 \
! jpegparse ! jpegdec ! fpsdisplaysink video-sink="autovideosink" sync=false fullscreen-overlay=true

"""
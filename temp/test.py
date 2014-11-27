
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk, GstPbutils

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo


GObject.threads_init()
Gst.init(None)


class ErrorHandler:
	def on_error(self,bus, msg):
		print('on_error():', msg.parse_error())

class Test:
    def __init__(self):
        self.root = Gtk.Window()
        self.root.connect('destroy', self.quit)
        self.root.set_default_size(800, 450)

        self.drawingarea = Gtk.DrawingArea()
        self.root.add(self.drawingarea)

        self.errorhandler = ErrorHandler()

        self.createPipeline()
       
    def createPipeline(self):
     	self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.errorhandler.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('autovideosrc', None)
        self.sink = Gst.ElementFactory.make('autovideosink', None)

        # Add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.sink)

        self.src.link(self.sink)


    def run(self):
        self.root.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.drawingarea.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)


webcam = Test()
webcam.run()

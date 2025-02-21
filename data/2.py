import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

# Create the pipeline
pipeline = Gst.parse_launch(
    "filesrc location=input.mp4 ! decodebin name=decoder "
    "decoder. ! queue ! videoconvert ! avenc_mpeg4 ! mp4mux name=mux ! filesink location=output.mp4 "
    "decoder. ! queue ! audioconvert ! avenc_aac ! mux."
)

# Seek to 150 seconds
pipeline.set_state(Gst.State.PAUSED)
success = pipeline.seek_simple(
    Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 150 * Gst.SECOND
)

if success:
    print("Seek successful, starting playback...")
    pipeline.set_state(Gst.State.PLAYING)
else:
    print("Seek failed!")

# Wait for completion
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS | Gst.MessageType.ERROR)

# Cleanup
pipeline.set_state(Gst.State.NULL)


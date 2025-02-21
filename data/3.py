import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

def run_gstreamer(input_file, start_time, end_time, output_file):
    # Create a GStreamer pipeline that separates video and audio streams
    pipeline = Gst.parse_launch(f'filesrc location={input_file} ! decodebin name=dec '
                                f'! queue ! videoconvert ! mp4mux name=mux ! filesink location={output_file} '
                                f'dec. ! queue ! audioconvert ! audioresample ! mux.')

    # Get the source element (filesrc) and set the start time
    source = pipeline.get_by_name('filesrc0')

    # Set the start time (in seconds)
    source.set_property('start-time', start_time * Gst.SECOND)
    
    # Set the end time (in seconds) by controlling the EOS event after the given duration
    pipeline.set_state(Gst.State.PLAYING)
    
    # Wait for the pipeline to finish or reach the end of the specified time range
    pipeline.get_bus().poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    
    pipeline.set_state(Gst.State.NULL)

# Using float times
run_gstreamer('input.mp4', 150.0, 168.0, 'output_float_copy.mp4')



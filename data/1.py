import subprocess

# Using floats with -c copy
subprocess.run([
    'ffmpeg',
    '-i', 'original.mp4',
    '-ss', '150.0',
    '-to', '168.0',
    '-c', 'copy',
    'output_float_copy.mp4'
])

# Using HH:MM:SS with -c copy
subprocess.run([
    'ffmpeg',
    '-i', 'original.mp4',
    '-ss', '00:02:30',
    '-to', '00:02:48',
    '-c', 'copy',
    'output_hhmmss_copy.mp4'
])




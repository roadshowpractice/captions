from setuptools import setup, find_packages

setup(
    name='captions',
    version='0.1.0',
    packages=find_packages(where='lib'),
    package_dir={'': 'lib'},
    include_package_data=True,
    install_requires=[
        # Add from requirements.txt or leave empty for now
    ],
    scripts=[
        'bin/call_captions.py',
        'bin/call_clips.py',
        'bin/call_download.py',
        'bin/call_router.py',
        'bin/call_untar_and_sort.py',
        'bin/call_watermark.py',
        'bin/composite_timeline.py',
        'bin/convert_screenshots.py',
        'bin/dispatch.py',
        'bin/download_images.py',
        'bin/untar_and_list.py'
    ],
)

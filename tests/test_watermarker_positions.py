import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(os.path.dirname(current_dir), 'lib', 'python_utils')
sys.path.append(lib_dir)

from watermarker2 import _resolve_position, looks_like_filename
import watermarker2


class TestWatermarkPositions(unittest.TestCase):
    def test_bottom_right_is_in_frame(self):
        position = _resolve_position(
            ('right', 'bottom'),
            clip_size=(120, 40),
            video_size=(720, 1280),
            edge_padding=8,
        )
        self.assertEqual(position, (592, 1232))



    def test_safe_margins_are_applied_for_edges(self):
        position = _resolve_position(
            ('right', 'bottom'),
            clip_size=(120, 40),
            video_size=(720, 1280),
            edge_padding=8,
            safe_margins={"right": 20, "bottom": 120, "left": 20, "top": 20},
        )
        self.assertEqual(position, (580, 1120))

    def test_looks_like_filename_catches_urls_and_download_names(self):
        self.assertTrue(looks_like_filename('http://example.com/media'))
        self.assertTrue(looks_like_filename('videoplayback'))
        self.assertTrue(looks_like_filename('download_123'))
        self.assertFalse(looks_like_filename('creator_name'))

    def test_invalid_position_falls_back_safely(self):
        position = _resolve_position(
            ('wat', 'nope'),
            clip_size=(120, 40),
            video_size=(720, 1280),
            edge_padding=8,
        )
        self.assertEqual(position, (8, 8))

    def test_dynamic_timestamp_clip_uses_frame_function_fallback(self):
        original_video_clip = watermarker2.VideoClip
        original_build_text_clip = watermarker2._build_text_clip

        class FakeTextClip:
            def __init__(self):
                self.size = (100, 20)

            def with_position(self, _position):
                return self

            def get_frame(self, _):
                return "frame"

        class FakeVideoClip:
            def __init__(self, make_frame=None, frame_function=None):
                if make_frame is not None:
                    raise TypeError("unexpected keyword")
                self.frame_function = frame_function

            def with_duration(self, duration):
                self.duration = duration
                return self

        try:
            watermarker2.VideoClip = FakeVideoClip
            watermarker2._build_text_clip = lambda *_args, **_kwargs: FakeTextClip()

            fake_video = type("FakeVideo", (), {"duration": 5})()
            clip = watermarker2._build_dynamic_timestamp_clip(
                {
                    "timestamp_color": "white",
                    "timestamp_position": ("left", "top"),
                    "font": "Arial",
                    "font_size": 20,
                },
                fake_video,
                (720, 1280),
                8,
                {"left": 8, "top": 8, "right": 8, "bottom": 8},
            )

            self.assertEqual(clip.duration, 5)
            self.assertEqual(clip.frame_function(0), "frame")
        finally:
            watermarker2.VideoClip = original_video_clip
            watermarker2._build_text_clip = original_build_text_clip


if __name__ == '__main__':
    unittest.main()

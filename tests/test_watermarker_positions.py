import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(os.path.dirname(current_dir), 'lib', 'python_utils')
sys.path.append(lib_dir)

from watermarker2 import _resolve_position, looks_like_filename


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


if __name__ == '__main__':
    unittest.main()

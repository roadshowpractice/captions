import os
import json
import unittest
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(os.path.dirname(current_dir), 'bin')
sys.path.append(bin_dir)

from expand_metadata import expand_metadata
from generate_timeline import generate_timeline


class TestTimelineGeneration(unittest.TestCase):
    def test_generate(self):
        metadata = os.path.join(current_dir, 'stamped3', 'metadata.json')
        id_map = os.path.join(current_dir, 'identity_map.json')
        expanded_out = os.path.join(current_dir, 'expanded_metadata.json')
        timeline_out = os.path.join(current_dir, 'generated_timeline.json')

        expanded = expand_metadata(metadata, id_map, expanded_out)
        timeline = generate_timeline(expanded_out, timeline_out)

        self.assertTrue(len(expanded) > 0)
        self.assertIn('identity', expanded[0])
        self.assertIn('canvas', timeline)

if __name__ == '__main__':
    unittest.main()

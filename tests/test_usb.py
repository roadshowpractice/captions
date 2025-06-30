import unittest
import os
import logging

# Ensure bin directory is in path for imports
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(root_dir, 'bin'))

from call_download import detect_target_usb

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestUSBDetection(unittest.TestCase):
    def test_write_kilroy(self):
        path = detect_target_usb({})
        if not path:
            self.skipTest('No USB path detected')
        test_file = os.path.join(path, 'kilroy.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('Kilroy was here')
            with open(test_file, 'r') as f:
                content = f.read().strip()
            self.assertEqual(content, 'Kilroy was here')
            logger.info('Kilroy was here')
        except PermissionError:
            self.skipTest('Permission denied writing to USB')
        finally:
            try:
                os.remove(test_file)
            except Exception:
                pass

if __name__ == '__main__':
    unittest.main()

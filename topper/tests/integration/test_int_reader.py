import unittest
from pathlib import Path
from unittest.mock import patch

from topper.file_io import FileReader


class TestIntFileReader(unittest.TestCase):
    def test_read_file_ok(self):
        file_reader = FileReader(path=Path(__file__).parent / 'data/listen-YYYYMMDD.log',
                                 checkpoint_dir=Path(__file__).parent / 'data/')
        with self.assertLogs(file_reader.logger, level='WARNING') as cm, \
                patch.object(FileReader, 'check_file_name', retrun_value=True):
            result = list(file_reader.read_file())  # cast result to list because read_file returns an generator
            expected = [('FR', '19016308', '819736552'),
                        ('FR', '19016308', '819746552'),
                        ('SE', '2996444', '67494308'),
                        ('ML', '51790731', '126357563')]
            self.assertEqual(expected, result)
            self.assertIn('WARNING:topper.file_io:Line is incorrect. The country \'VJ\' doesn\'t exists', cm.output)
            self.assertIn('WARNING:topper.file_io:Line is incorrect. The country \'UR\' doesn\'t exists', cm.output)


if __name__ == '__main__':
    unittest.main()

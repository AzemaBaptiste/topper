import unittest

from topper.__main__ import Topper
from topper.utils.parser import parse_args


class TestMain(unittest.TestCase):
    def test_main(self):
        topper = Topper(arguments=parse_args(['--landing_folder', 'landing_folder',
                                              '--checkpoint_directory', 'checkpoint', '--output_directory', 'output']))

        topper.main()


if __name__ == '__main__':
    unittest.main()

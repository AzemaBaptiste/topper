import unittest

from topper.__main__ import Topper
from topper.utils.parser import parse_args


class MyTestCase(unittest.TestCase):
    """
    Unit test main
    """

    def setUp(self):
        self.topper = Topper(arguments=parse_args(['--landing_folder', 'landing_folder',
                                                   '--checkpoint_directory', 'checkpoint', '--output_directory',
                                                   'output']))

    def test_constructor(self):
        self.assertEqual('country', self.topper.mode)
        self.assertEqual(7, self.topper.nb_days)


if __name__ == '__main__':
    unittest.main()

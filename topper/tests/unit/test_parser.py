import unittest

from topper.utils.parser import create_parser


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

    def test_arguments_no_mode(self):
        parsed = self.parser.parse_args(['--landing_folder', 'landing_folder',
                                         '--checkpoint_directory', 'checkpoint', '--output_directory', 'output'])

        self.assertEqual(parsed.landing_folder, 'landing_folder')
        self.assertEqual(parsed.checkpoint_directory, 'checkpoint')
        self.assertEqual(parsed.output_directory, 'output')
        self.assertEqual(parsed.mode, 'country')

    def test_arguments_mode_user(self):
        parsed = self.parser.parse_args(['--landing_folder', 'landing_folder',
                                         '--checkpoint_directory', 'checkpoint', '--output_directory', 'output',
                                         '--mode', 'user'])

        self.assertEqual(parsed.landing_folder, 'landing_folder')
        self.assertEqual(parsed.checkpoint_directory, 'checkpoint')
        self.assertEqual(parsed.output_directory, 'output')
        self.assertEqual(parsed.mode, 'user')

    def test_arguments_invalid_mode(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--landing_folder', 'landing_folder',
                                    '--checkpoint_directory', 'checkpoint', '--output_directory', 'output',
                                    '--mode', 'invalid'])

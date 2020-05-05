import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call

from topper.file_io import FileReader, FolderReader, FileWriter


class TestFileReader(unittest.TestCase):
    """
    Unit tests of file utils
    """

    def setUp(self):
        self.file_reader = FileReader(path='my/path/file.log', checkpoint_dir='checkpoint_directory/')

    def test_reader_constructor(self):
        self.assertIsNotNone(self.file_reader)
        self.assertEqual(Path('my/path/file.log'), self.file_reader.path)
        self.assertEqual(Path('checkpoint_directory/'), self.file_reader._checkpoint_dir)

    def test__countries_iso2(self):
        list_countries = self.file_reader._countries_iso2()
        # At least 240 countries
        self.assertLess(240, len(list_countries))

        # France and Spain in list
        self.assertTrue('FR' in list_countries)
        self.assertTrue('ES' in list_countries)

    def test__check_file_name(self):
        # Mock reject_file method
        self.file_reader.reject_file = MagicMock(return_value=None)

        # doesn't match regex
        result_ko = self.file_reader.check_file_name('bad_name.log')
        self.assertFalse(result_ko)

        # Date out of range: 41th of february
        result_bad_date = self.file_reader.check_file_name('listen-20200241.log')
        self.assertFalse(result_bad_date)

        # test OK
        result_ok = self.file_reader.check_file_name('listen-20200211.log')
        self.assertTrue(result_ok)

    def test_read_file(self):
        # Read file OK
        with patch('topper.file_io.FileReader._parse_log_file', MagicMock()) as mock_parse_file:
            self.file_reader.check_file_name = MagicMock(return_value=True)
            self.file_reader.path = PathMock('valid.log', is_a_file=True)
            self.file_reader.read_file()
            mock_parse_file.assert_called()

        # Read file KO
        with patch('topper.file_io.FileReader.reject_file', MagicMock()) as mock_reject_file, \
                self.assertLogs(self.file_reader.logger, level='WARNING') as cm:
            self.file_reader.check_file_name = MagicMock(return_value=False)
            self.file_reader.path = PathMock('invalid.log', is_a_file=True)
            self.file_reader.read_file()
            mock_reject_file.assert_called()
            self.assertEqual(['ERROR:topper.file_io:Can\'t process file=invalid.log'], cm.output)

    def test_parse_file(self):
        self.file_reader._countries_iso2 = MagicMock(return_value=['FR', 'GB', 'ES'])
        # 2 valid lines, 2 invalid lines (invalid pattern + country not in list)
        open_mock_return_value = ['12|15|FR', '2929292902|120200120|ES', '12|FR', '12|15|AA']
        opener = mock_open(read_data='\n'.join(open_mock_return_value))
        with patch("pathlib.Path.open", opener) as mock_open_file, \
                self.assertLogs(self.file_reader.logger, level='WARNING') as cm:
            result = list(self.file_reader._parse_log_file())
            mock_open_file.assert_called()
            self.assertEqual([('FR', '15', '12'), ('ES', '120200120', '2929292902')], result)
            self.assertEqual(['WARNING:topper.file_io:Line is incorrect. Pattern invalid: 12|FR\n',
                              "WARNING:topper.file_io:Line is incorrect. The country 'AA' doesn't exists"],
                             cm.output)

    def test_reject_file(self):
        with patch("pathlib.Path.rename") as mock_path_rename, \
                patch("pathlib.Path.mkdir") as mock_path_mkdir:
            self.file_reader.reject_file()
            mock_path_mkdir.assert_called()
            mock_path_rename.assert_called_with(self.file_reader._checkpoint_dir /
                                                self.file_reader.REJECT_FOLDER / 'file.log')

    def test_move_file_archive(self):
        with patch("pathlib.Path.rename") as mock_path_rename, \
                patch("pathlib.Path.mkdir") as mock_path_mkdir:
            self.file_reader.move_file_archive()
            mock_path_mkdir.assert_called()
            mock_path_rename.assert_called_with(self.file_reader._checkpoint_dir /
                                                self.file_reader.ARCHIVE_FOLDER / 'file.log')

    def test_move_file_top_days(self):
        with patch("pathlib.Path.rename") as mock_path_rename, \
                patch("pathlib.Path.mkdir") as mock_path_mkdir, \
                patch("pathlib.Path.is_file", return_value=True):
            self.file_reader.path = Path('my/path/listen-20200213.log')
            self.file_reader.move_file_top_days()
            mock_path_mkdir.assert_called()
            mock_path_rename.assert_called_with(self.file_reader._checkpoint_dir /
                                                self.file_reader.CURRENT_FOLDER / 'listen-20200213.log')


class TestFolderReader(unittest.TestCase):
    """
    Unit tests of folder utils
    """

    def setUp(self):
        self.folder_reader = FolderReader(_path_dir='my/path/', _checkpoint_directory='checkpoint/')

    def test_list_files(self):
        # Mock reject_file method
        self.folder_reader.reject_file = MagicMock(return_value=None)

        # Empty folder
        with patch('pathlib.Path.iterdir', return_value=[]):
            self.assertEqual([], self.folder_reader._list_files())

        # 1 match, 1 not match
        mock_files = [PathMock('bad_format.log', True), PathMock('listen-20200211.log', True)]
        with patch('pathlib.Path.iterdir', return_value=mock_files), \
             patch('topper.file_io.FileReader.reject_file', return_value=None):
            result = self.folder_reader._list_files()
            get_name = list(map(lambda x: x.path.name, result))
            self.assertEqual(['listen-20200211.log'], get_name)

    def test_read_folder_days(self):
        # Test KO: path is a file
        self.folder_reader._path_dir = PathMock(name='my_file.log', is_a_file=True, is_a_dir=False)
        with self.assertLogs(self.folder_reader.logger, level='WARNING') as cm:
            self.folder_reader.read_folder_current()
            self.assertEqual(['ERROR:topper.file_io:Path provided is not a directory: my_file.log'], cm.output)

        # Test: 2 valid files
        self.folder_reader._path_dir = PathMock(name='my_path/', is_a_file=False, is_a_dir=True)
        self.folder_reader._list_files = MagicMock(return_value=[FileReader('my_path/1.log', '/'),
                                                                 FileReader('my_path/2.log', '/')])

        with patch('topper.file_io.FileReader.read_file', MagicMock(return_value=True)) as mock_read_file:
            self.folder_reader.read_folder_current()
            mock_read_file.assert_has_calls([call(), call()])  # 2 calls because 2 valid files

    def test_archive_old_files(self):
        today = datetime.today()

        three_days_ago_str = (today - timedelta(days=3)).strftime('%Y%m%d')
        two_days_ago_str = (today - timedelta(days=2)).strftime('%Y%m%d')

        # 1 match, 1 not match
        mock_files = [Path('listen-{}.log'.format(three_days_ago_str), is_a_file=True),
                      Path('listen-{}.log'.format(two_days_ago_str), is_a_file=True)]
        with patch('pathlib.Path.iterdir', return_value=mock_files), \
             patch('topper.file_io.FileReader.move_file_archive', return_value=None) as mock_archive, \
                patch("pathlib.Path.is_dir", return_value=True):
            self.folder_reader.archive_old_files(3)

            # Only 1 call on move archive: file 3 days ago
            mock_archive.assert_called_once()


class TestFileWriter(unittest.TestCase):
    """
    Unit tests of Writer utils
    """

    def setUp(self):
        self.file_writer = FileWriter(path='my/path/file.txt')

    def test_write_result(self):
        expected_line1 = call('FR|13,3:16,2:20192323,1\n')
        expected_line2 = call('GB|1313,42:16,28:23,14\n')
        input_data = {'FR': [(13, 3), (16, 2), (20192323, 1)], 'GB': [(1313, 42), (16, 28), (23, 14)]}
        open_mock = mock_open()
        with patch("builtins.open", open_mock, create=True), \
             patch("pathlib.Path.mkdir") as mock_path_mkdir:
            self.file_writer.write_result(input_data)
            mock_path_mkdir.assert_called()
            open_mock.assert_called_with(Path("my/path/file.txt"), mode="w")
            open_mock.return_value.write.assert_has_calls([expected_line1, expected_line2])


class PathMock:
    def __init__(self, name, is_a_file=True, is_a_dir=False):
        self.name = name
        self.is_a_file = is_a_file
        self.is_a_dir = is_a_dir

    def __repr__(self):
        return self.name

    def is_file(self):
        return self.is_a_file

    def is_dir(self):
        return self.is_a_dir


if __name__ == '__main__':
    unittest.main()

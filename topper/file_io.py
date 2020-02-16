import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from topper.utils.logging import get_logger


class FileReader:
    """
    Utils class managing read, parse and move of data files
    """
    REJECT_FOLDER = 'errors'
    ARCHIVE_FOLDER = 'archive'
    CURRENT_FOLDER = 'current'

    def __init__(self, path, checkpoint_dir):
        self.path = Path(path)
        self._checkpoint_dir = Path(checkpoint_dir)
        self.logger = get_logger(__name__)

    def read_file(self):
        """
        Parse valid files and returns content as a generator
        :return: Generator(tuple(country, user_id, sng_id))
        """
        if self.path.is_file() and self.check_file_name(self.path.name):
            return self._parse_log_file()
        else:
            self.logger.error('Can\'t process file={}'.format(self.path))
            self.reject_file()
            return None

    def check_file_name(self, file_name):
        """
        Control formatting of the file name using regex and either date in file name exists or not
        :param file_name: string: name to test
        :return: Date of the file, False if invalid file
        """
        regex_filename = r'listen-(\d{8}).log'
        # Extract date with regex
        date_str = re.findall(regex_filename, file_name)
        if len(date_str) == 1:
            # Check if the date in file name can be parsed as Date object
            try:
                return datetime.strptime(date_str[0], '%Y%m%d')
            except ValueError:
                self.logger.warning('Date cannot be parsed in file name: {}'.format(file_name))
                return False
        else:
            # otherwise it's a bad format
            self.logger.warning('File name is invalid {}'.format(file_name))
            return False

    def _parse_log_file(self):
        """
        Parse the input file and yield results as a tuple (country, user_id, song_id)
        :return: list(tuple(str, str, str)): tuple of (country, user_id, song_id)
        """
        regex_line = r'^\d+\|\d+\|[A-Z]{2}$'

        countries = self._countries_iso2()

        with self.path.open() as file:

            for raw_line in file.readlines():
                if re.match(regex_line, raw_line):
                    sng_id, user_id, country = raw_line.rstrip().split(sep='|')
                    if country in countries:
                        yield country, user_id, sng_id
                    else:
                        self.logger.warning('Line is incorrect. The country \'{}\' doesn\'t exists'.format(country))
                else:
                    self.logger.warning('Line is incorrect. Pattern invalid: {}'.format(raw_line))

    def reject_file(self):
        """
        Move invalid files to error folder
        """
        if not (self._checkpoint_dir / self.REJECT_FOLDER).exists():
            (self._checkpoint_dir / self.REJECT_FOLDER).mkdir(parents=True)
        self.path.rename(self._checkpoint_dir / self.REJECT_FOLDER / self.path.name)

    def move_file_archive(self):
        """
        Move old files to archive folder
        """
        if not (self._checkpoint_dir / self.ARCHIVE_FOLDER).exists():
            (self._checkpoint_dir / self.ARCHIVE_FOLDER).mkdir(parents=True)
        self.path.rename(self._checkpoint_dir / self.ARCHIVE_FOLDER / self.path.name)

    def move_file_top_days(self):
        """
        Move current files to top_days folder
        """
        if self.path.is_file() and self.check_file_name(self.path.name):
            if not (self._checkpoint_dir / self.CURRENT_FOLDER).exists():
                (self._checkpoint_dir / self.CURRENT_FOLDER).mkdir(parents=True)
            self.path.rename(self._checkpoint_dir / self.CURRENT_FOLDER / self.path.name)

    @staticmethod
    def _countries_iso2():
        """
        Returns a list of countries as iso2 codes
        :return: list: list of country codes
        """
        current_dir = Path(__file__).parent
        countries_path = current_dir / 'resources' / 'countries.json'
        with open(countries_path) as raw_file:
            json_data = json.load(raw_file)
            code_list = list(map(lambda country: country['code'], json_data))
            return code_list


class FolderReader:
    """
    Utils class managing folders of data files
    """

    def __init__(self, _path_dir, _checkpoint_directory):
        self._path_dir = Path(_path_dir)
        self._checkpoint_directory = _checkpoint_directory
        self.logger = get_logger(__name__)

    def process_folder_landing(self):
        """
        Process landing folder and move valid files to folder `current`, invalid ones to `errors`
        :return:
        """
        if self._path_dir.is_dir():
            for valid_file in self._list_files():
                valid_file.move_file_top_days()
        else:
            self.logger.error('Path provided is not a directory: {}'.format(self._path_dir))

    def read_folder_current(self):
        """
        Scan every files in path self._path_dir and returns every valid files.
        Invalid files are thrown to errors' folder
        :return: list(pathlib.Path): list of files to process
        """
        if self._path_dir.is_dir():
            res = []

            for valid_file in self._list_files():
                res.append(valid_file.read_file())
            return res
        else:
            self.logger.error('Path provided is not a directory: {}'.format(self._path_dir))
            return None

    def _list_files(self):
        """
        Get files to process and send invalid files to error folder
        :return: a list of valid pathlib.Path
        """
        file = []
        for file_name in self._path_dir.iterdir():
            file_reader = FileReader(path=str(file_name), checkpoint_dir=self._checkpoint_directory)
            if file_name.is_file() and file_reader.check_file_name(file_name.name):
                file.append(file_reader)
            else:
                file_reader.reject_file()
        return file

    def archive_old_files(self, days):
        """
        Move files oldest than X days from process to archive folder
        :param days: number of days to keep
        """
        oldest_day = datetime.today() - timedelta(days=days)
        if self._path_dir.is_dir():
            for file_name in self._path_dir.iterdir():
                file_reader = FileReader(self._path_dir / file_name, self._checkpoint_directory)
                file_date = file_reader.check_file_name(file_name.name)
                if file_date < oldest_day:
                    file_reader.move_file_archive()


# pylint: disable=too-few-public-methods
class FileWriter:
    """
    Utils class managing write of output files
    """

    def __init__(self, path):
        self._path = Path(path)
        self.logger = get_logger(__name__)

    def write_result(self, dict_result):
        """
        Write result file
        :param dict_result: dictionary to write
        """
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
        with open(self._path, mode='w') as output_file:
            for country, data in dict_result.items():
                format_song_nber_list = map(lambda x: '{},{}'.format(x[0], x[1]), data)

                line = '{c}|'.format(c=country)
                line += ':'.join(format_song_nber_list)
                line += '\n'
                output_file.write(line)

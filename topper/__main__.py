import sys
from datetime import datetime
from pathlib import Path

from topper.file_io import FolderReader, FileReader, FileWriter
from topper.process import Process
from topper.utils.logging import get_logger
from topper.utils.parser import parse_args


# pylint: disable=too-few-public-methods
class Topper:
    """
    Main class running Topper application
    """

    def __init__(self, arguments):
        self.checkpoint_directory = Path(arguments.checkpoint_directory)
        self.logger = get_logger(__name__)
        self.landing_folder = Path(arguments.landing_folder)
        self.current_folder = self.checkpoint_directory / FileReader.CURRENT_FOLDER
        self.output_directory = Path(arguments.output_directory)
        self.mode = arguments.mode
        self.nb_days = 7

    def main(self):
        """
        Main processing
        """
        self.logger.info('Topper')
        start_time = datetime.now()

        # Check landing folder & move valid landing to `current` folder
        landing_folder = FolderReader(self.landing_folder, self.checkpoint_directory)
        landing_folder.process_folder_landing()

        # Move file in `current` folder > X days
        current_reader = FolderReader(self.current_folder, self.checkpoint_directory)
        current_reader.archive_old_files(days=self.nb_days)

        # Read folder `current`
        days_data = current_reader.read_folder_current()

        if days_data:
            # Compute top days
            process = Process(self.mode)
            process.reduce_days(days_data)  # data Group by the mode (user or country)
            res = process.get_top50()  # Sort and get top50

            # Save result
            output_file = self.output_directory / '{mode}_top50_{d}.txt'.format(mode=self.mode,
                                                                                d=datetime.now().strftime('%Y%m%d'))
            result_writer = FileWriter(output_file)
            result_writer.write_result(res)

        # End
        now = datetime.now()
        time_run = (now - start_time).total_seconds()
        self.logger.info('Processing time: {} seconds'.format(time_run))


def main():
    """main"""
    args = parse_args(args=sys.argv[1:])
    Topper(args).main()


if __name__ == '__main__':
    main()

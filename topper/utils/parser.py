"""
Argument parser
"""
import argparse


def create_parser():
    """
    Parser
    :return: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--landing_folder',
        help='Folder of file reception',
        required=True
    )
    parser.add_argument(
        '--checkpoint_directory',
        help='Directory used to persist data across days',
        required=True
    )
    parser.add_argument(
        '--output_directory',
        help='Path to output directory',
        required=True
    )
    parser.add_argument(
        '--mode',
        help='Path to output directory',
        required=False,
        default='country',
        choices=['country', 'user']
    )
    return parser


def parse_args(args):
    """
    Parse arguments
    :param args: raw args
    :return: Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args=args)

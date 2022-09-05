import argparse


def make_arguments_parser():
    """Create an argparse command line argument parser.
    """
    parser = argparse.ArgumentParser(description='Oslo Dawn Patrol road captains scheduler bot.')

    # Debug mode
    parser.add_argument(
        "-d", 
        "--debug", 
        help="Enable debug mode. Bot will not send messages to Discord.", 
        action="store_true")

    return parser


def parse_command_line_arguments(parser, logger):
    """Parse arguments supplied at command line.
    """
    logger.debug('Read command line arguments.')
    args = parser.parse_args()
    logger.debug('Command line arguments are %s', args.__repr__())
    
    return args
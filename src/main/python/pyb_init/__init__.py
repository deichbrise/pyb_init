__version__ = '${version}'

from docopt import docopt


def entry_point():
    parsed_command_line = docopt(doc=__doc__, version=__version__)
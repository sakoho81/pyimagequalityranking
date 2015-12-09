"""
File:        script_options.py
Author:      Sami Koho (sami.koho@gmail.com

Description:
This file contains the various generic command line options
for controlling the behaviour of the PyImageQuality software.
In addition, some specific parameters are defined in the
filters.py file
"""

import argparse

from pyimq import filters, myimage


def get_quality_script_options(arguments):
    parser = argparse.ArgumentParser(
        description="Command line arguments for the "
                    "image quality ranking software"
    )

    parser.add_argument(
        "--file",
        help="Defines a path to the image files",
        default=None
    )
    parser.add_argument(
        "--working-directory",
        dest="working_directory",
        help="Defines the location of the working directory",
        default="/home/sami/Pictures/Quality"
    )
    parser.add_argument(
        "--mode",
        choices=["file", "directory", "analyze", "plot"],
        action="append",
        help="The argument containing the functionality of the main program"
             "You can concatenate actions by defining multiple modes in a"
             "single command, e.g. --mode=directory --mode=analyze"
    )
    # Parameters for controlling the way plot functionality works.
    parser.add_argument(
        "--result",
        default="average",
        choices=["average", "fskew", "ientropy", "fentropy", "fstd", "fkurtosis", "fpw", "fmean", "icv"],
        help="Tell how you want the results to be calculated."
    )
    parser.add_argument(
        "--npics",
        type=int,
        default=9,
        help="Define how many images are shown in the plots"
    )

    parser = filters.get_options(parser)
    parser = myimage.get_options(parser)
    return parser.parse_args(arguments)





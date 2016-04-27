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
        choices=["average", "fskew", "ientropy", "fentropy", "fstd",
                 "fkurtosis", "fpw", "fmean", "icv", "meanbin"],
        help="Tell how you want the results to be calculated."
    )
    parser.add_argument(
        "--npics",
        type=int,
        default=9,
        help="Define how many images are shown in the plots"
    )

    parser = filters.get_common_options(parser)
    parser = myimage.get_options(parser)
    return parser.parse_args(arguments)


def get_power_script_options(arguments):
    """
    Command line arguments for the power.py script that is used to calculate
    1D power spectra of images within a directory.
    """
    parser = argparse.ArgumentParser(
        description="Command line options for the power.py script that can be"
                    "used to save the power spectra of images within a "
                    "directory"
    )
    parser.add_argument(
        "--working-directory",
        dest="working_directory",
        help="Defines the location of the working directory",
        default="/home/sami/Pictures/Quality"
    )
    parser.add_argument(
        "--image-size",
        dest="image_size",
        type=int,
        default=512
    )
    parser = filters.get_common_options(parser)
    parser = myimage.get_options(parser)
    return parser.parse_args(arguments)


def get_subjective_ranking_options(arguments):
    """
    Command line arguments for the subjective.py script that can be used
    to obtain subjective opinion scores for image quality.
    """
    parser = argparse.ArgumentParser(
        description="Command line arguments for the "
                    "subjective image quality ranking"
                    "script."
    )
    parser.add_argument(
        "--working-directory",
        dest="working_directory",
        help="Defines the location of the working directory",
        default="/home/sami/Pictures/Quality"
    )

    return parser.parse_args(arguments)



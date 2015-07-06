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

    # Parameters for controlling how image files are handled
    parser.add_argument(
        "--imagej",
        help="Defines wheter the image are in ImageJ tiff format, "
             "and thus contain the pixel size info etc in the TIFF tags. "
             "By default true",
        action="store_true"
    )
    parser.add_argument(
        "--rgb-channel",
        help="Select which channel in an RGB image is to be used for quality"
             " analysis",
        dest="rgb_channel",
        type=int,
        choices=[0, 1, 2],
        default=1
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
    # File filtering for batch mode processing
    parser.add_argument(
        "--average-filter",
        dest="average_filter",
        type=int,
        default=0,
        help="Analyze only images with similar amount of detail, by selecting a "
             "grayscale average pixel value threshold here"
    )
    parser.add_argument(
        "--file-filter",
        dest="file_filter",
        default=None,
        help="Define a common string in the files to be analysed"
    )

    from filters import get_filter_options
    parser = get_filter_options(parser)
    return parser.parse_args(arguments)





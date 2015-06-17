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
        action="append"
    )

    # Image I/O
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
    parser.add_argument(
        "--file-filter",
        dest="file_filter",
        default=None,
        help="Define a common string in the files to be analysed"
    )
    parser.add_argument(
        "--result",
        default="average",
        choices=["average", "fskew", "ientropy", "fentropy", "fstd", "fkurtosis", "fpw", "fmean"],
        help="Tell how you want the results to be calculated."
    )
    parser.add_argument(
        "--npics",
        type=int,
        default=9
    )

    from filters import get_filter_options
    parser = get_filter_options(parser)
    return parser.parse_args(arguments)





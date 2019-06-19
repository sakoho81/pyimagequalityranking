#!/usr/bin/env python
# -*- python -*-

"""
File:   test_rgb_channel_select.py
Author: Sami Koho (sami.koho@gmail.com)

Description:
A small utility for testing the RGB channel extraction functionality
"""
import sys
import os

from pyimq.myimage import MyImage


path_prefix = "/home/sami/Pictures/Quality/GFP_PFCA_dsRedLNCaP_in_Col/"


def main():
    if len(sys.argv) < 3:
        print("You must define a path to an image and a color channel to " \
              "extract")
        sys.exit(1)

    path = sys.argv[1]
    channel = int(sys.argv[2])
    assert 0 <= channel <= 2

    real_path = os.path.join(path_prefix, path)
    assert os.path.isfile(real_path)

    image = MyImage.get_generic_image(real_path)
    one_channel = image.get_channel(channel)
    one_channel.show()

if __name__ == "__main__":
    main()
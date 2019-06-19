"""
File:        utils.py
Author:      sami.koho@gmail.com

Description:
Various sorts of small utilities for the PyImageQuality software.
Contains all kinds of code snippets that did not find a home in
the main modules.
"""

from scipy import ndimage
import numpy
from matplotlib import pyplot as plt
import os


def rescale_to_min_max(data, data_min, data_max):
    """
    A function to rescale image intensities to range, define by
    data_min and data_max input parameters.

    :param data:        Input image (Numpy array)
    :param data_min:    Minimum pixel value. Can be any type of a number
                        (preferably of the same type with the data.dtype)
    :param data_max:    Maximum pixel value
    :return:            Return the rescaled array
    """
    # Check if image is an RGB image
    if len(data.shape) == 3:
        for i in range(data.shape[2]):
            if abs(data[:, :, i].max()) > abs(data[:, :, i].min()) or data_min == 0:
                data[:, :, i] = data_max / data.max()*data[:, :, i]
            else:
                data[:, :, i] = data_min / data.min()*data[:, :, i]
        return data

    else:
        if abs(data.max()) > abs(data.min()) or data_min == 0:
            return data_max / data.max()*data
        else:
            return data_min / data.min()*data


def analyze_accumulation(x, fraction):
    """
    Analyze the accumulation by starting from the end of the data.
    """
    assert 0.0 < fraction <= 1.0
    final = fraction*x.sum()
    index = 1
    while x[-index:].sum() < final:
        index += 1
    return index


def calculate_entropy(data):
    """
    Calculate the Shannon entropy for data
    """
    # Calculate histogram
    histogram = ndimage.histogram(
        data,
        data.min(),
        data.max(), 50)
    # Exclude zeros
    histogram = histogram[numpy.nonzero(histogram)]
    # Normalize histogram bins to sum to one
    histogram = histogram.astype(float)/histogram.sum()
    return -numpy.sum(histogram*numpy.log2(histogram))


def show_pics_from_disk(filenames, title="Image collage"):
    """
    A utility for creating a collage of images, to be shown
    in a single plot. The images are loaded from disk according
    to the provided filenames:
    :param filenames:   A list containing the image filenames
    :param title:       Name of the plot
    :return:            Nothing
    """
    if len(filenames) > 1:
        if 4 < len(filenames) <= 9:
            fig, subplots = plt.subplots(3, 3)
        elif 9 < len(filenames) <= 16:
            fig, subplots = plt.subplots(4, 4)
        elif 16 < len(filenames) <= 25:
            fig, subplots = plt.subplots(5, 5)
        elif 25 < len(filenames) <= 36:
            fig, subplots = plt.subplots(6, 6)
        else:
            fig, subplots = plt.subplots(2, 2)

        #fig.title(title)
        i = 0
        j = 0
        k = 0
        while k < len(filenames):
            j = 0
            while j < subplots.shape[1] and k < len(filenames):
                print(filenames[i+j])
                subplots[i, j].imshow(plt.imread(filenames[k]), cmap=plt.cm.hot)
                subplots[i, j].set_title(os.path.basename(filenames[k]))
                subplots[i, j].axis("off")
                k += 1
                j += 1
            i += 1
        plt.subplots_adjust(wspace=-0.5, hspace=0.2)
        plt.suptitle(title, size=16)
        plt.show()

    else:
        plt.imshow(plt.imread(filenames))
        plt.axis("off")
        plt.show()
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
    # Return array with max value in the original image scaled to correct
    # range
    if abs(data.max()) > abs(data.min()) or data_min == 0:
        return data_max / data.max()*data
    else:
        return data_min / data.min()*data

def analyze_accumulation(x, fraction):
    assert 0.0 < fraction <= 1.0
    final = fraction*x.sum()
    index = 1
    while x[-index:].sum() < final:
        index += 1
    return index

def calculate_entropy(data):
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
    if len(filenames) > 1:
        if len(filenames) > 4:
            fig, subplots = plt.subplots(3, 3)
        elif len(filenames) > 9:
            fig, subplots = plt.subplots(4, 4)
        else:
            fig, subplots = plt.subplots(2, 2)

        #fig.title(title)
        i = 0
        j = 0
        k = 0
        while k < len(filenames):
            j = 0
            while j < subplots.shape[1] and k < len(filenames):
                print filenames[i+j]
                subplots[i, j].imshow(plt.imread(filenames[k]), cmap=plt.cm.hot)
                subplots[i, j].set_title(k)
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
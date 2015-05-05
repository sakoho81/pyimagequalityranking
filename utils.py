from scipy import ndimage
import numpy

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
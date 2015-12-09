"""
File:        filters.py
Author:      Sami Koho (sami.koho@gmail.com)

Description:
This file contains the filters that are used for calculating the
image quality parameters in the PyImageQuality software.
-   The LocalImageQuality class is used to run spatial domain
    analysis. It calculates the Shannon entropy value at a
    masked part of an image
-   The FrequencyQuality class is used to calculate statistical
    quality parameters in the frequency domain. The calculations
    are based on the analysis of the tail of the 1D power spect-
    rum.
"""

import numpy
from scipy import ndimage, fftpack, stats
from matplotlib import pyplot as plt
from math import floor
import argparse

from pyimq import external as radprof, utils

from pyimq.myimage import MyImage as Image


def get_options(parser):
    """
    Command-line options for the image-quality filters
    """
    assert isinstance(parser, argparse.ArgumentParser)
    group = parser.add_argument_group("Filters", "Options for the quality filters")
    group.add_argument(
        "--power-averaging",
        dest="power_averaging",
        choices=["radial", "additive"],
        default="additive"
    )
    group.add_argument(
        "--normalize-power",
        dest="normalize_power",
        action="store_true"

    )
    group.add_argument(
        "--use-mask",
        dest="use_mask",
        action="store_true"
    )
    group.add_argument(
        "--invert-mask",
        dest="invert_mask",
        action="store_true"
    )
    return parser


class Filter(object):
    """
    A base class for a filter utilizing Image class object
    """
    def __init__(self, image, options, physical=False, verbal=False):

        assert isinstance(image, Image)
        self.options = options

        if image.is_rgb():
            self.data = image.get_channel(self.options.rgb_channel)

        self.data = image

        self.spacing = self.data.get_spacing()
        self.dimensions = self.data.get_dimensions()
        self.physical = physical
        self.verbal = verbal

    def set_physical_coordinates(self):
        self.physical = True

    def set_pixel_coordinates(self):
        self.physical = False


class LocalImageQuality(Filter):
    """
    This is a filter for quantifying  image quality, based on the calculation
    of Shannon entropy at image neighborhoods that contain the highest amount
    of detail.
    """

    def __init__(self, image, options, physical=False, verbal=False):

        Filter.__init__(self, image, options, physical, verbal)

        self.data_temp = None
        self.kernel_size = []

    def set_smoothing_kernel_size(self, size):

        if isinstance(size, list):
            assert len(size) == len(self.spacing)
            sizes = size
        elif isinstance(size, float) or isinstance(size, int):
            sizes = []
            for i in self.spacing:
                sizes.append(size)
        else:
            print "Unknown size type"
            return

        if self.physical is True:
            for i in range(len(sizes)):
                self.kernel_size[i] = sizes[i]/self.spacing[i]
                assert self.kernel_size[i] < self.dimensions[i]
        else:
            self.kernel_size = sizes
            assert self.kernel_size < self.dimensions, \
                "Kernel can not be larger than image"

    def run_mean_smoothing(self, return_result=False):
        """
        Mean smoothing is used to create a mask for the entropy calculation
        """

        assert len(self.kernel_size) == len(self.dimensions)
        self.data_temp = ndimage.uniform_filter(self.data[:], size=self.kernel_size)

        if return_result:
            return Image(self.data_temp, self.spacing)

    def calculate_entropy(self):
        """
        Returns the Shannon entropy value of an image.
        """
        # Calculate histogram
        histogram = ndimage.histogram(
            self.data_temp,
            self.data_temp.min(),
            self.data_temp.max(), 50
        )
        # Exclude zeros
        histogram = histogram[numpy.nonzero(histogram)]
        # Normalize histogram bins to sum to one
        histogram = histogram.astype(float)/histogram.sum()
        return -numpy.sum(histogram*numpy.log2(histogram))

    def find_sampling_positions(self):
        """
        Create a mask by finding pixel positions in the smoothed image
        that have pixel values higher than 80% of the maximum value.
        """
        peaks = numpy.percentile(self.data_temp, 80)
        mask = numpy.where(self.data_temp >= peaks, 1, 0)
        if self.options.invert_mask:
            return numpy.invert(mask.astype(bool))
        else:
            return mask

    def calculate_image_quality(self, kernel=None, show=False):
        """
        Calculate an estimate for image quality, based on the
        Shannon entropy measure. options.use_mask switch can
        be used to limit the entropy calculation to detailed
        parts of the image.
        """
        if self.options.use_mask:
            if kernel is not None:
                self.set_smoothing_kernel_size(kernel)

            assert len(self.kernel_size) != 0

            if self.data_temp is None:
                self.run_mean_smoothing()

            positions = self.find_sampling_positions()
            self.data_temp = self.data[:][numpy.nonzero(positions)]
            if show:
                Image(self.data[:]*positions, self.spacing).show()
        else:
            self.data_temp = self.data[:]

        return self.calculate_entropy()


class FrequencyQuality(Filter):
    """
    A filter for calculated image-quality related parameters in the frequency
    domain. First a one-dimensional power spectrum is calculated for an image,
    after which various types of statistics are calculated for the power
    spectrum tail (frequencies > 40% of Nyquist)
    """
    def __init__(self, image, options, physical=False, verbal=False):

        Filter.__init__(self, image, options, physical=physical, verbal=verbal)

        # Additive form of power spectrum calculation requires a square shaped
        # image
        if self.options.power_averaging == "additive":
            self.crop()

        self.simple_power = None
        self.power = None
        self.kernel_size = []

    def set_image(self, image):
        self.data = image

    def calculate_power_spectrum(self, show=False):
        """
        A function that is used to calculate a centered 2D power spectrum.
        Additionally the power spectrum can be normalized by image dimensions
        and image intensity mean, if necessary.
        """
        self.power = numpy.abs(fftpack.fftshift(fftpack.fft2(self.data[:])))**2
        if self.options.normalize_power:
            dims = self.data[:].shape[0]*self.data[:].shape[1]
            mean = numpy.mean(self.data[:])
            self.power = self.power/(dims*mean)

        if show:
            Image(numpy.log10(self.power), self.spacing).show()

    def calculate_radial_average(self, bin_size=2, show=False):
        """
        Convert a 2D centered power spectrum into 1D by averaging spectral
        power at different radiuses from the zero frequency center
        """
        bin_centers, average = radprof.azimuthalAverage(
            self.power,
            binsize=bin_size,
            returnradii=True,
            normalize=True
        )
        dx = self.data.get_spacing()[0]

        size = int(float(self.power.shape[0])/2)
        f_k = (bin_centers/size) * (1.0/(2*dx))

        self.simple_power = [f_k, average]

        if show:
            plt.plot(numpy.log10(self.simple_power[0]))
            plt.ylabel("Average power")
            plt.xlabel("Frequency")
            plt.show()

    def calculate_summed_power(self, show=False):
        """
        Calculate a 1D power spectrum fro 2D power spectrum, by summing all rows and
        columns, and then summing negative and positive frequencies, to form a
        N/2+1 long 1D array. This approach is significantly faster to calculate
        than the radial average.
        """

        sum = numpy.zeros(self.power.shape[0])
        for i in range(len(self.power.shape)):
            sum += numpy.sum(self.power, axis=i)
        zero = floor(float(sum.size)/2)
        sum[zero+1:] = sum[zero+1:]+sum[:zero-1][::-1]
        sum = sum[zero:]
        dx = self.data.get_spacing()[0]
        f_k = numpy.linspace(0, 1, sum.size)*(1.0/(2*dx))

        self.simple_power = [f_k, sum]

        if show:
            plt.plot(self.simple_power[0], self.simple_power[1], linewidth=2, color="red")
            plt.ylabel("Total power")
            plt.yscale('log')
            plt.xlabel('Frequency')
            plt.show()

    def analyze_power_spectrum(self, show_intermediate=False, show=False):
        """
        Run the image quality analysis on the power spectrum
        """
        assert self.data is not None, "Please set an image to process"
        self.calculate_power_spectrum(show=show_intermediate)

        # Choose a method to calculate 1D power spectrum
        if self.options.power_averaging == "radial":
            self.calculate_radial_average(show=show_intermediate)
        elif self.options.power_averaging == "additive":
            self.calculate_summed_power(show=show_intermediate)
        else:
            raise NotImplementedError

        # Extract the power spectrum tail
        hf_sum = self.simple_power[1][self.simple_power[0] > .4*self.simple_power[0].max()]

        # Calculate parameters
        f_th = self.simple_power[0][self.simple_power[0] > .4*self.simple_power[0].max()][-utils.analyze_accumulation(hf_sum, .2)]
        mean = numpy.mean(hf_sum)
        std = numpy.std(hf_sum)
        entropy = utils.calculate_entropy(hf_sum)
        nm_th = 1.0e9/f_th
        pw_at_high_f = numpy.mean(self.simple_power[1][self.simple_power[0] > .9*self.simple_power[0].max()])
        skew = stats.skew(numpy.log(hf_sum))
        kurtosis = stats.kurtosis(hf_sum)

        if show:
            print "The mean is: %e" % mean
            print "The std of the power spectrum tail is: %e" % std
            print "The entropy of frequencies is %e" % entropy
            print "The threshold distance is %f nanometers" % nm_th
            print "Power at high frequencies %e" % pw_at_high_f

        return [mean, std, entropy, nm_th, pw_at_high_f, skew, kurtosis]

    def show_all(self):
        """
        A small utility to show a plot of the 2D and 1D power spectra
        """
        fig, subplots = plt.subplots(1, 2)
        if self.power is not None:
            subplots[0].imshow(numpy.log10(self.power))
        if self.simple_power is not None:
            index = int(len(self.simple_power[0])*.4)
            #subplots[1].plot(self.simple_power[0][index:], self.simple_power[1][index:], linewidth=1)
            subplots[1].plot(self.simple_power[0], self.simple_power[1], linewidth=1)
            subplots[1].set_yscale('log')
        plt.show()

    def crop(self):
        """
        Crops the input image into a square. This is required by the additive
        1D power spectrum calculation routine
        """
        dims = self.data[:].shape

        if dims[0] > dims[1]:
            diff = int(0.5*(dims[0]-dims[1]))
            self.data = Image(self.data[:][diff: -diff, :], self.data.get_spacing())
        elif dims[1] > dims[0]:
            diff = int(0.5*(dims[1]-dims[0]))
            self.data = Image(self.data[:][:, diff: -diff], self.data.get_spacing())



class SpectralMoments(FrequencyQuality):

    def calculate_percent_spectrum(self):
        self.simple_power[1] /= (self.simple_power[1].sum()/100)

    def calculate_spectral_moments(self, show_intermediate=False):
        """
        Run the image quality analysis on the power spectrum
        """
        assert self.data is not None, "Please set an image to process"
        self.calculate_power_spectrum(show=show_intermediate)

        # Choose a method to calculate 1D power spectrum
        if self.options.power_averaging == "radial":
            self.calculate_radial_average(show=show_intermediate)
        elif self.options.power_averaging == "additive":
            self.calculate_summed_power(show=show_intermediate)
        else:
            raise NotImplementedError

        self.calculate_percent_spectrum()

        bin_index = numpy.arange(1, self.simple_power[1].shape[0]+1)

        return (self.simple_power[1]*numpy.log10(bin_index)).sum()


class BrennerImageQuality(Filter):

    def __init__(self, image, options, physical=False, verbal=False):

        Filter.__init__(self, image, options, physical, verbal)

    def calculate_brenner_quality(self):
        data = self.data.get_array()
        rows = data.shape[0]
        columns = data.shape[1]-2
        temp = numpy.zeros((rows, columns))

        temp[:] = ((data[:, 0:-2] - data[:, 2:])**2)

        return temp.sum()
















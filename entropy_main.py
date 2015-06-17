import sys
import os

import csv
import datetime
import pandas

import filters
import myimage
import utils
import script_options


def main():
    
    options = script_options.get_quality_script_options(sys.argv[1:])
    path = options.working_directory
    file_path = None
    csv_data = None

    print "Mode option is %s" % options.mode

    if "file" in options.mode:

        assert options.file is not None, "You have to specify a file with a " \
                                         "--file option"
        path = os.path.join(path, options.file)
        assert os.path.isfile(path)
        if options.imagej:
            image = myimage.MyImage.get_image_from_imagej_tiff(path)
        else:
            image = myimage.MyImage.get_generic_image(path)
        if image.is_rgb():
            image = image.get_channel(options.rgb_channel)
            print "The shape is %s" % str(image.images.shape)

        task = filters.LocalImageQuality(image, options)
        task.set_smoothing_kernel_size(150)
        entropy = task.calculate_image_quality(show=True)
        task2 = filters.ImageResolution(image, options)
        finfo = task2.analyze_power_spectrum(show=True, power="radial")

        print "SPATIAL MEASURES:"
        print "The entropy value of %s is %f" % (path, entropy)
        print "ANALYSIS OF THE POWER SPECTRUM TAIL"
        print "The mean is: %e" % finfo[0]
        print "The std is: %e" % finfo[1]
        print "The entropy is %e" % finfo[2]
        print "The threshold distance is %f nanometers" % finfo[3]
        print "Power at high frequencies %e" % finfo[4]
        print "The skewness is %f" % finfo[5]
        print "The kurtosis is %f" % finfo[6]

    if "directory" in options.mode:
        # d - mode requires a directory
        assert os.path.isdir(path), path

        # Create output directory
        output_dir = datetime.datetime.now().strftime("%Y-%m-%d")+'_EIQ_output'
        output_dir = os.path.join(options.working_directory, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        date_now = datetime.datetime.now().strftime("%H-%M-%S")
        file_name = date_now + '_EIQ_out' + '.csv'
        file_path = os.path.join(output_dir, file_name)
        output_file = open(file_path, 'wt')
        output_writer = csv.writer(output_file, quoting=csv.QUOTE_NONNUMERIC, delimiter=",")
        output_writer.writerow(
            ("Filename", "tEntropy", "fMean", "fSTD", "fEntropy",
             "fTh", "fMaxPw", "Skew", "Kurtosis"))

        for image_name in os.listdir(path):
            if options.file_filter is None or options.file_filter in image_name:
                real_path = os.path.join(path, image_name)
                if not os.path.isfile(real_path) or not real_path.endswith((".jpg", ".tif", ".tiff", ".png")):
                    continue
                if options.imagej:
                    image = myimage.MyImage.get_image_from_imagej_tiff(real_path)
                else:
                    image = myimage.MyImage.get_generic_image(real_path)
                if image.is_rgb():
                    image = image.get_channel(options.rgb_channel)

                task = filters.LocalImageQuality(image, options)
                task.set_smoothing_kernel_size(100)
                entropy = task.calculate_image_quality()

                task2 = filters.ImageResolution(image, options)
                results = task2.analyze_power_spectrum()

                results.insert(0, entropy)
                results.insert(0, os.path.join(path, image_name))

                output_writer.writerow(results)

                print "Done analyzing %s" % image_name

        output_file.close()
        print "The results were saved to %s" % file_path

    if "analyze" in options.mode:
        # In "analyze" mode a previously created data file will be opened here.
        # The data file should be located in the working directory, and the
        # file name should be specified with the --file command line argument
        if file_path is None:
            assert options.file is not None, "You have to specify a data file" \
                                             "with the --file option"
            path = os.path.join(options.working_directory, options.file)
            print path
            file_path = path
            assert os.path.isfile(path), "Not a valid file %s" % path
            assert path.endswith(".csv"), "Unknown suffix %s" % path.split(".")[-1]

        csv_data = pandas.read_csv(file_path)
        csv_data["cv"] = csv_data.fSTD/csv_data.fMean
        csv_data["SpatEntNorm"] = csv_data.tEntropy/csv_data.tEntropy.max()
        csv_data["SpectMean"] = csv_data.fMean/csv_data.fMean.max()
        csv_data["SpectSTDNorm"] = csv_data.fSTD/csv_data.fSTD.max()
        csv_data["InvSpectSTDNorm"] = 1- csv_data.SpectSTDNorm
        csv_data["SpectEntNorm"] = csv_data.fEntropy/csv_data.fEntropy.max()
        csv_data["SkewNorm"] = 1 - abs(csv_data.Skew)/abs(csv_data.Skew).max()
        csv_data["KurtosisNorm"] = abs(csv_data.Kurtosis)/abs(csv_data.Kurtosis).max()
        csv_data["SpectHighPowerNorm"] = csv_data.fMaxPw/csv_data.fMaxPw.max()

        # Create output directory
        output_dir = datetime.datetime.now().strftime("%Y-%m-%d")+'_EIQ_output'
        output_dir = os.path.join(options.working_directory, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        date_now = datetime.datetime.now().strftime("%H-%M-%S")
        file_name = date_now + '_EIQ_analyze_out' + '.csv'
        file_path = os.path.join(output_dir, file_name)

        csv_data.to_csv(file_path)
        print "The results were saved to %s" % file_path

    if "plot" in options.mode:

        if csv_data is None:
            path = os.path.join(options.working_directory, options.file)
            assert os.path.isfile(path), "Not a valid file %s" % path
            assert path.endswith(".csv"), "Unknown suffix %s" % path.split(".")[-1]
            csv_data = pandas.read_csv(path)
        if options.result == "average":
            csv_data["Average"] = csv_data[["SpatEntNorm", "SkewNorm", "InvSpectSTDNorm"]].mean(axis=1)
            csv_data.sort(column="Average", ascending=False, inplace=True)
        elif options.result == "fskew":
            csv_data.sort(column="SkewNorm", ascending=False, inplace=True)
        elif options.result == "fentropy":
            csv_data.sort(column="SpectEntNorm", ascending=False, inplace=True)
        elif options.result == "ientropy":
            csv_data.sort(column="SpatEntNorm", ascending=False, inplace=True)
        elif options.result == "fstd":
            csv_data.sort(column="SpectSTDNorm", ascending=False, inplace=True)
        elif options.result == "fkurtosis":
            csv_data.sort(column="KurtosisNorm", ascending=False, inplace=True)
        elif options.result == "fpw":
            csv_data.sort(column="SpectHighPowerNorm", ascending=False, inplace=True)
        elif options.result == "fmean":
            csv_data.sort(column="SpectHighPowerNorm", ascending=False, inplace=True)
        else:
            print "Unknown results sorting method %s" % options.result
            sys.exit()

        best_pics = csv_data["Filename"].head(options.npics).as_matrix()
        worst_pics = csv_data["Filename"].tail(options.npics).as_matrix()
        utils.show_pics_from_disk(best_pics, title="BEST PICS")
        utils.show_pics_from_disk(worst_pics, title="WORST PICS")

        csv_data.to_csv(path, index=False)



if __name__ == "__main__":
    main()
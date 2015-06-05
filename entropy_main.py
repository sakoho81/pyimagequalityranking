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

    print "Mode option is %s" % options.mode

    if options.mode == "file":
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

        print "The entropy value of %s is %f" % (path, entropy)
        print "The mean is: %e" % finfo[0]
        print "The std is: %e" % finfo[1]
        print "The entropy of frequencies is %e" % finfo[2]
        print "The threshold distance is %f nanometers" % finfo[3]
        print "Power at highest frequency %e" % finfo[4]

    elif options.mode == "directory":
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
             "fTh", "fMaxPw", "Skew"))

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
                results = task2.analyze_power_spectrum(power="radial")

                results.insert(0, entropy)
                results.insert(0, os.path.join(path, image_name))

                output_writer.writerow(results)

                print "Done analyzing %s" % image_name

        output_file.close()
        print "The results were saved to %s" % file_path

    elif options.mode == "analyze":
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

        data = pandas.read_csv(file_path)
        data["cv"] = data.fSTD/data.fMean
        data["SpatEntNorm"] = data.tEntropy/data.tEntropy.max()
        data["SpectSTDNorm"] = data.fSTD/data.fSTD.max()
        data["SpectEntNorm"] = data.fEntropy/data.fEntropy.max()
        data["SkewNorm"] = 1 - abs(data.Skew)/abs(data.Skew).max()

        if options.result == "average":
            data["Average"] = data[["SpectSTDNorm", "SpatEntNorm"]].mean(axis=1)
            data.sort(column="Average", ascending=False, inplace=True)
        elif options.result == "fskew":
            data.sort(column="SkewNorm", ascending=False, inplace=True)
        elif options.result == "fentropy":
            data.sort(column="SpectEntNorm", ascending=False, inplace=True)
        elif options.result == "ientropy":
            data.sort(column="SpatEntNorm", ascending=False, inplace=True)
        elif options.result == "fstd":
            data.sort(column="SpectSTDNorm", ascending=False, inplace=True)
        else:
            print "Unknown results sorting method %s" % options.result
            sys.exit()

        best_pics = data["Filename"].head(options.npics).as_matrix()
        worst_pics = data["Filename"].tail(options.npics).as_matrix()
        utils.show_pics_from_disk(best_pics, title="BEST PICS")
        utils.show_pics_from_disk(worst_pics, title="WORST PICS")

        # Create output directory
        output_dir = datetime.datetime.now().strftime("%Y-%m-%d")+'_EIQ_output'
        output_dir = os.path.join(options.working_directory, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        date_now = datetime.datetime.now().strftime("%H-%M-%S")
        file_name = date_now + '_EIQ_analyze_out' + '.csv'
        file_path = os.path.join(output_dir, file_name)

        data.to_csv(file_path)
        print "The results were saved to %s" % file_path

    elif options.mode == "plot":
        path = os.path.join(options.working_directory, options.file)
        assert os.path.isfile(path), "Not a valid file %s" % path
        assert path.endswith(".csv"), "Unknown suffix %s" % path.split(".")[-1]

        data = pandas.read_csv(path)
        if options.result == "average":
            data["Average"] = data[["SpectSTDNorm", "SpatEntNorm"]].mean(axis=1)
            data.sort(column="Average", ascending=False, inplace=True)
        elif options.result == "fskew":
            data.sort(column="SkewNorm", ascending=False, inplace=True)
        elif options.result == "fentropy":
            data.sort(column="SpectEntNorm", ascending=False, inplace=True)
        elif options.result == "ientropy":
            data.sort(column="SpatEntNorm", ascending=False, inplace=True)
        elif options.result == "fstd":
            data.sort(column="SpectSTDNorm", ascending=False, inplace=True)
        else:
            print "Unknown results sorting method %s" % options.result
            sys.exit()

        best_pics = data["Filename"].head(options.npics).as_matrix()
        worst_pics = data["Filename"].tail(options.npics).as_matrix()
        utils.show_pics_from_disk(best_pics, title="BEST PICS")
        utils.show_pics_from_disk(worst_pics, title="WORST PICS")



if __name__ == "__main__":
    main()
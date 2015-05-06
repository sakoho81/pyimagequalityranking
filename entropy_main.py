import sys

import os
import csv
import datetime
import pandas

import filters
import myimage
import utils



path_prefix = "/home/sami/Pictures/Quality"


def main():
    if len(sys.argv) < 2 or "-" not in sys.argv[1]:
        print "Usage: python entropy_main.py [-mode] path"
        print "In which mode can be either file (f) or directory (d)"
        print "The path is a relative path from %s default path prefix"
        print "You can leave the path empty if the preset folder is OK."
        sys.exit(1)

    mode = sys.argv[1]
    if len(sys.argv) < 3:
        path = path_prefix
    else:
        path = os.path.join(path_prefix, sys.argv[2])
    file_path = None

    if 'f' in mode:
        image = myimage.MyImage.get_image_from_imagej_tiff(path)

        task = filters.LocalImageQuality(image)
        task.set_smoothing_kernel_size(100)
        entropy = task.calculate_image_quality()
        task2 = filters.ImageResolution(image)
        finfo = task2.analyze_power_spectrum()

        print "The entropy value of %s is %f" % (path, entropy)
        print "The mean is: %e" % finfo[0]
        print "The std is: %e" % finfo[1]
        print "The entropy of frequencies is %e" % finfo[2]
        print "The threshold distance is %f nanometers" % finfo[3]
        print "Power at highest frequency %e" % finfo[4]

    elif 'd' in mode:
        # d - mode requires a directory
        assert os.path.isdir(path), path

        # Create output directory
        output_dir = datetime.datetime.now().strftime("%Y-%m-%d")+'_EIQ_output'
        output_dir = os.path.join(path_prefix, output_dir)
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
            if image_name.endswith(('.tif', '.tiff')) and "STED" in image_name:
                real_path = os.path.join(path, image_name)
                image = myimage.MyImage.get_image_from_imagej_tiff(real_path)

                task = filters.LocalImageQuality(image)
                task.set_smoothing_kernel_size(100)
                entropy = task.calculate_image_quality()

                task2 = filters.ImageResolution(image)
                results = task2.analyze_power_spectrum()

                results.insert(0, entropy)
                results.insert(0, os.path.join(path, image_name))

                output_writer.writerow(results)

                print "Done analyzing %s" % image_name

        output_file.close()
        print "The results were saved to %s" % file_path

    elif 'a' in mode:
        if file_path is None:
            file_path = path
            assert os.path.isfile(path), "Not a valid file %s" % path
            assert path.endswith(".csv"), "Unknown suffix %s" % path.split(".")[-1]



        data = pandas.read_csv(file_path)
        data["cv"] = data.fSTD/data.fMean
        data["SpatEntNorm"] = data.tEntropy/data.tEntropy.max()
        data["SpectEntNorm"] = data.fEntropy/data.fEntropy.max()
        data["SkewNorm"] = 1 - abs(data.Skew)/abs(data.Skew).max()

        data["Result"] = data[["SpectEntNorm", "SpatEntNorm", "SkewNorm"]].mean(axis=1)
        data.sort(column="Result", ascending=False, inplace=True)

        best_pics = data["Filename"].head(9).as_matrix()
        worst_pics = data["Filename"].tail(9).as_matrix()
        utils.show_pics_from_disk(best_pics, title="BEST PICS")
        utils.show_pics_from_disk(worst_pics, title="WORST PICS")

        # Create output directory
        output_dir = datetime.datetime.now().strftime("%Y-%m-%d")+'_EIQ_output'
        output_dir = os.path.join(path_prefix, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        date_now = datetime.datetime.now().strftime("%H-%M-%S")
        file_name = date_now + '_EIQ_analyze_out' + '.csv'
        file_path = os.path.join(output_dir, file_name)

        data.to_csv(file_path)
        print "The results were saved to %s" % file_path


    else:
        print "Unknown mode parameter %s. Please choose -f, -d or -a" % mode





if __name__ == "__main__":
    main()
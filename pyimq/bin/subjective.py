#!/usr/bin/env python
# -*- python -*-

"""
File: subjective.py
Author: Sami Koho (sami.koho@gmail.com)

Description:

A utility script for performing subjective image rankings. One image is
displayed at a time, after which it is ranked on 1-5 scale, 5 being the
best and 1 the worst. The script can be run multiple times to collect
several ranking results in a single csv file.
"""

import sys, os
import pandas
import matplotlib.pyplot as plt
import pyimq.script_options as script_options


def main():

    print "Hello"
    options = script_options.get_subjective_ranking_options(sys.argv[1:])
    path = options.working_directory
    index = 0
    assert os.path.isdir(path), path

    # Create or open a csv file
    output_dir = path
    file_name = "subjective_ranking_scores.csv"
    file_path = os.path.join(output_dir, file_name)

    if os.path.exists(file_path):
        csv_data = pandas.read_csv(file_path)
        # Append a new result column
        for column in csv_data:
            if "Result" in column:
                index += 1
    else:
        csv_data = pandas.DataFrame()
        file_names = []
        # Get valid file names
        for image_name in os.listdir(path):
            real_path = os.path.join(path, image_name)
            if not os.path.isfile(real_path) or not real_path.endswith((".jpg", ".tif", ".tiff", ".png")):
                continue
            file_names.append(image_name)
        csv_data["Filename"] = file_names

    result_name = "Result_" + index
    results = []

    plt.ion()

    print "Images are graded on a scale 1-5, where 1 denotes a very bad image " \
          "and 5 an excellent image"

    for image_name in csv_data["Filename"]:
        real_path = os.path.join(path, image_name)
        image = plt.imread(real_path)
        image *= (255.0/image.max())

        plt.imshow(image, cmap=plt.cm.gray)

        success = False
        while not success:
            result = int(raw_input("Give grade: ").trim())
            if 1 <= result <= 5:
                success = True
                results.append(result)
            else:
                print "Please give a numeric grade 1-5."

    csv_data[result_name] = results
    csv_data.to_csv(file_path, index=False)

if __name__ == "__main__":
    main()












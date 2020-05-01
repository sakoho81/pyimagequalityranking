# PyImageQualityRanking 

## An Image quality ranking tool for Microscopy

*PyImageQualityRanking* is a small software utility that allows the ordering/sorting of image datasets, according to image-quality related statistical parameters. The software is distributed under BSD open source license.

### How does it work?
The purpose of this tool is to extract image-quality related statistics from a series of images (a dataset) that can then be used to sort/rank the images according to their relative quality. Such tool could be used for example to find the highest-quality images in a dataset, or to identify and discard low-quality images. The purpose of the software is to figure out, whether certain images were clearly better than the rest in the dataset, or vice versa.

Our aim was to develop a simple tool that would not involve any complex mathematical models or training schemes – but that could still provide robust quality-related measures, that could be taken advantage of in a variety of applications. The analysis was also intended to be simple and fast, to allow its easy integration to any image-processing workflow – including real-time during-acquisition analysis. 

*PyImageQualityRanking* software implements two kinds of parameters to rank image quality. 

1. The quality of the image histogram (contrast) is estimated by a Shannon entropy measure, that is calculated at a masked region of an image, to allow the comparison of images with varying content. 
2. The image detail is estimated in the frequency domain, by calculating a number of parameters from the power spectrum. The calculations focus on the power spectrum tail (usually >40% of max. frequency)
3. The software also contains our implementations of two microscopy autofocus metrics that were used as comparison for our method.

### How do I install it?
*PyImageQualityRanking* was written utilizing standard SciPy scientific libraries. The software should thus work on all the common operating systems. *PyImageQualityRanking* is distributed as a standard python package and it can be installed using the **setup.py** script. However, you should make sure that you have installed the [SciPy libraries](http://www.scipy.org/install.html) in the computer's Python environment. Typically, if using Anaconda distribution etc. these libraries should have been installed by default.

Please refer to the Wiki page for usage examples.

### Contribution guidelines ###

The *PyImageQualityRanking* is distributed under [BSD open-source license](https://bitbucket.org/sakoho81/pyimagequalityranking/wiki/License). You can use the software in any way you like; we would just ask you to aknowledge our work:

[*Koho, S., Fazeli, E., Eriksson, J.E. & Hänninen, P.E. (2016) Image Quality Ranking Method for Microscopy. Scientific Reports, 6, 28962.*](http://www.nature.com/articles/srep28962)

All kinds of contributions: new features, bug fixes, documentation, usage examples etc. are welcome.

### Contacts ###

Sami Koho <sami.koho@gmail.com>




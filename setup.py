from setuptools import setup, find_packages

setup(
    name='pyimq',
    version='0.1',
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'pandas', 'matplotlib'],
    entry_points={
        'console_scripts': [
            'pyimq.main = pyimq.bin.main:main',
            'pyimq.util.blurseq = pyimq.bin.utils.create_blur_sequence:main',
            'pyimq.util.imseq = pyimq.bin.utils.create_photo_test_set:main',
            'pyimq.subjective = pyimq.bin.subjective:main',
            'pyimq.power = pyimq.bin.power:main'
        ]
    },
    platforms=["any"],
    url='https://github.org/sakoho81/pyimagequalityranking',
    download_url="https://github.com/sakoho81/pyimagequalityranking/archive/v0.1.tar.gz",
    license='BSD',
    author='Sami Koho',
    author_email='sami.koho@gmail.com',
    description='pyimq is a small software utility that allows '
                'the ordering/sorting of image datasets, according to '
                'image-quality related statistical parameters',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)

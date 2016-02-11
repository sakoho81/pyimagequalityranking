from setuptools import setup, find_packages

setup(
    name='PyImageQualityRanking',
    version='0.1',
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'pandas', 'matplotlib'],
    entry_points={
        'console_scripts': [
            'pyimq.main = pyimq.bin.__main__:main',
            'pyimq.blurseq = pyimq.bin.create_blur_sequence:main'
        ]
    },
    platforms=["any"],
    url='https://bitbucket.org/sakoho81/pyimagequalityranking',
    license='BSD',
    author='Sami Koho',
    author_email='sami.koho@gmail.com',
    description='PyImageQualityRanking is a small software utility that allows '
                'the ordering/sorting of image datasets, according to '
                'image-quality related statistical parameters'
)

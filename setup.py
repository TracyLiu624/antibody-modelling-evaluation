from setuptools import setup, find_packages

setup(
    name='cdr-eval',
    version='0.1',
    packages=find_packages(['cdr_eval/*']),
    install_requires=[
        'pandas',
        'PyYAML',
        'biopython',
        'numpy',
        'matplotlib',
        'seaborn',
    ],
    author='Tracy Liu, ChuNan Liu',
    author_email='ruiqi.liu.19@alumni.ucl.ac.uk',
    description='Evaluate CDRs using ProFit and abpackingangle',
    classifiers=[
        'Intended Audience :: Bioinformaticians',
        'Programming Language :: Python :: 3.8',
    ],
)
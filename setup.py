from setuptools import setup

setup(
    name='Fuzzi_Moss',
    version='0.1',
    packages=['fuzzi_moss'],
    package_dir={'': './' },
    url='https://github.com/twsswt/fuzzi-moss',
    license='',
    author='Tom Wallis, Tim Storer',
    author_email='',
    description='Fuzzing for Modelling Variance in Socio-technical Systems',
    test_suite='tests.unittests',
    tests_require=['mock']
)

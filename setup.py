from setuptools import setup

setup(
    name='Fuzzi_Moss',
    version='0.1',
    packages=['fuzzi_moss'],
    package_dir={'': '.'},
    url='https://github.com/twsswt/fuzzi-moss',
    dependency_links=[
        'https://github.com/twsswt/pydysofu/tarball/master#egg=pydysofu-0.1'],
    license='',
    author='Tom Wallis, Tim Storer',
    author_email='twallisgm@gmail.com',
    description='Fuzzing for Modelling Variance in Socio-technical Systems',
    setup_requires=['nose', 'pydysofu', 'theatre_ag'],
    test_suite='nose.collector',
    tests_require=['mock', 'nose']
)

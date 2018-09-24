from distutils.core import setup

setup(
    name='flask-simple-salesforce',
    version='0.1',
    author='Rajesh Kaushik',
    author_email='rajesh.kaushik15@gmail.com',
    packages=['flask_simple_salesforce',],
#    url=about['__url__'],
#    license=about['__license__'],
#    description=about['__description__'],
#    long_description=textwrap.dedent(open('README.rst', 'r').read()),

    install_requires=[
        'simple-salesforce==0.74.2',
        'flask==1.0.2',
        'zeep==3.1.0'
    ],
    tests_require=[
        'pytest==3.6.3',
    ],
#    test_suite = 'nose.collector',

)

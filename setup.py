# Imports from python.  # NOQA
from setuptools import setup, find_packages  # NOQA
import os

from pip.req import parse_requirements
from pip.download import PipSession

REQS_RAW = parse_requirements('./requirements.txt', session=PipSession())

REQUIRES = [str(_.req) for _ in REQS_RAW]

DESCRIPTION = 'Data storage Django web application.'

REPO_URL = 'https://github.com/dallasmorningnews/django-datafreezer'

VERSION = '0.1.3'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-datafreezer',
    version=VERSION,
    description=DESCRIPTION,
    long_description=read('readme.md'),
    url=REPO_URL,
    download_url=REPO_URL + '/tarball/' + VERSION,
    author='Tyler Allyn Davis, The Dallas Morning News',
    author_email='tallyndavis@comcast.net',
    license='MIT',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    install_requires=REQUIRES,
    keywords=['django', 'csv', 'data', 'storage', 'journalism', 'javascript'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.1',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
    ],
    zip_safe=False,
)

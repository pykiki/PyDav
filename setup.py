try:
    # from setuptools import setup, find_packages
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
from setuptools.command.test import test as TestCommand
from setuptools.command.install import install as InstallCommand

version = "1.3"
requirements = "libxml2-dev libxslt-dev python-dev libcurl-openssl-dev"


class Install(InstallCommand):
    '''
    '''

    def run(self):
        '''
        params = "{install_params} {requirements}".format(
          install_params="install", requirements=requirements)
        cmd = "{command} {params}".format(command="apt-get", params=params)
        proc = subprocess.Popen(cmd, shell=True)
         proc.wait()
        '''
        InstallCommand.run(self)


class Test(TestCommand):
    '''
    '''

    user_options = [('pytest-args=', 'a', "")]

    def initialize_options(self):

        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):

        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):

        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


config = {
    'name': 'PyDav',
    'version': str(version),
    'description': 'CLI Webdav connector',
    'author': 'Maibach Alain',
    'author_email': 'alain.maibach@gmail.com',
    'maintainer': 'Maibach Alain',
    'url': 'https://github.com/pykiki',
    'download_url': 'https://github.com/pykiki/PyDav',
    'packages': ['PyDav'],
    'scripts': ['scripts/pydav-client'],
    'license': 'GNU GPLv3',
    'install_requires': [
        'argcomplete',
        'lxml',
        'pycurl',
        'webdavclient'
    ],
    'platforms': [
        'Linux',
        'OSX'],
    'zip_safe': False,
    'keywords': 'webdav, client, python, module, library, packet, nextcloud',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities']}

setup(**config)

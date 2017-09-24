try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'PyDav',
    'version': '1.0',
    'description': 'CLI Webdav connector',
    'author': 'Maibach Alain',
    'author_email': 'alain.maibach@gmail.com',
    'maintainer': 'Maibach Alain',
    'url': 'https://github.com/pykiki',
    'download_url': 'https://github.com/pykiki/PyDav',
    'packages': ['PyDav'],
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
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities']}

setup(**config)

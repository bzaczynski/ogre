#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2016 Bartosz Zaczynski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Installation:
$ python setup.py install

Install dependencies from the "requirements.txt" (skip already installed ones),
then build and copy the files to the egg directory in Python "site-packages".

Removal:
$ pip uninstall ogre

Development:
$ python setup.py develop [--uninstall]

Link current directory to "site-packages". This avoids the need to reinstall
after making modifications to the source code.

Testing:
$ python setup.py test
"""

import os

from setuptools import setup, find_packages


class Git:
    """Interface to git repositories."""

    def __init__(self, host, vendor):
        self.host = host
        self.vendor = vendor

    def home_url(self, repo):
        """Return https url for project overview page."""
        return f'https://{self.host}/{self.vendor}/{repo}'

    def clone_url(self, repo):
        """Return ssh url for git clone command."""
        return f'git@{self.host}:{self.vendor}/{repo}.git'

    def pip_url(self, repo, package, version):
        """Return setuptools dependency link for pip install command."""
        return 'git+ssh://git@{0}/{1}/{2}.git@{4}#egg={3}-{4}'.format(
            self.host,
            self.vendor,
            repo,
            package,
            version
        )


def path(*parts):
    """Return an absolute path to the given resource."""
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, *parts)


def find_version():
    """Return the value of ogre.__version__."""

    with open(path('ogre', '__init__.py')) as fp:
        exec(fp.read())

    return locals().get('__version__')


def main():

    git = Git('github.com', 'bzaczynski')

    setup(name='ogre',
          version=find_version(),
          description='Ognivo Report',
          long_description=open(path('README.md')).read(),
          author='Bartosz Zaczynski',
          author_email='bartosz.zaczynski@gmail.com',
          url=git.home_url('ogre'),
          download_url=git.clone_url('ogre'),
          license='The MIT License',
          dependency_links=[],
          install_requires=open(path('requirements.txt')).read().splitlines(),
          tests_require=open(path('requirements-test.txt')).read().splitlines(),
          test_suite='tests',
          packages=find_packages(exclude=['tests']),
          include_package_data=True,
          package_data={
              '': ['**/*.ttf'],
              'ogre': ['config.ini']
          },
          scripts=[
              'scripts/ogreport.py',
          ],
          zip_safe=True)


if __name__ == '__main__':
    main()

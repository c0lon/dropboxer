import os
from pathlib import Path
from setuptools import (
    find_packages,
    setup,
    )


here = os.path.dirname(os.path.abspath(__file__))
README = Path(os.path.join(here, 'README.md')).read_text()
CHANGES = Path(os.path.join(here, 'CHANGES.md')).read_text()
VERSION = Path(os.path.join(here, 'VERSION')).read_text().strip()

dependency_links = []
setup_requires = []
tests_require = []
install_requires = []
entry_points = {}

setup(name='dropboxer',
      description='',
      long_description=f'{README}\n\n{CHANGES}',
      version=VERSION,
      dependency_links=dependency_links,
      setup_requires=setup_requires,
      tests_require=tests_require,
      install_requires=install_requires,
      packages=find_packages('src'),
      package_dir={'': 'src'},
      package_data={'': '*'},
      entry_points=entry_points
      )

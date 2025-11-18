from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

required_packages = '''\
numpy attrs billiard cloudpickle dask dask-jobqueue
distributed gitpython jupyter traitlets
blosc pandas scipy python-xz
cryptography
'''.split()

class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        #install_pyrosetta()


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        #install_pyrosetta()

setup(
    name='pyrosetta-distributed',
    version='0.0.4',
    description='meta package to install dependecies needed for `pyrosetta.distributed` framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.pyrosetta.org/',
    author='Sergey Lyskov',
    license='Rosetta Software License',
    packages=['pyrosetta_distributed'],
    install_requires=required_packages,
    python_requires='>3.8',
    zip_safe=False,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)

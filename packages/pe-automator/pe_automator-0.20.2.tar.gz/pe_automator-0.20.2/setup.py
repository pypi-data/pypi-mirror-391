import os
from setuptools import setup
from setuptools import find_packages

requires = []
install_requires = [
    "bilby-pipe",
    "python-gitlab",
    "jinja2",
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "gwpy",
    "h5py",
    "streamlit",
    "streamlit-aggrid",
    "plotly",
    "GitPython",
    "click",
    "paramiko",
    "pymannkendall"
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="PE Automator",
    author="Yumeng Xu",
    author_email="yumeng.xu@ligo.org",
    description=("PE Automator is a Python package for automating the setup and execution of parameter estimation (PE) runs using Bilby Pipe."),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    keywords=['ligo', 'physics', 'gravity', 'signal processing', 'gravitational waves'],
    url="https://git.ligo.org/yumeng.xu/uib-o4a-catalog",
    install_requires=install_requires,
    scripts=["bin/pe_automator"],  # find_files('bin', relpath='./'),
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8'
)
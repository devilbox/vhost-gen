"""Pip configuration."""
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="vhost-gen",
    version="1.0.7",
    description="Configurable vHost generator for Apache 2.2, Apache 2.4 and Nginx.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cytopia",
    author_email="cytopia@everythingcli.org",
    url="https://github.com/devilbox/vhost-gen",
    install_requires=["pyyaml", "future"],
    scripts=[
        "bin/vhost-gen"
    ],
       project_urls={
        'Source Code': 'https://github.com/devilbox/vhost-gen',
        'Documentation': 'https://devilbox.readthedocs.io/en/latest/',
        'Bug Tracker': 'https://github.com/devilbox/vhost-gen/issues',
    },
 classifiers=[
        # https://pypi.org/classifiers/
        #
        # How mature is this project
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        "Intended Audience :: System Administrators",
        # Project topics
        'Topic :: Software Development :: Build Tools',
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        # License
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        # How does it run
        "Environment :: Console",
        # Where does it rnu
        "Operating System :: OS Independent",
    ],
 )

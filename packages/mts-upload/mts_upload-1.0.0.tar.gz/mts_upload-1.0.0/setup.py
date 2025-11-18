
from setuptools import setup

setup(
    name="mts-upload",
    version="1.0.0",
    description="Uploads files to confluence with support for expands.",
    author="Ben Bastianelli",
    author_email="benbastianelli@gmail.com",
    packages=["mts_upload"],
    entry_points={
        'console_scripts': [
            'upload=mts_upload.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["markdown >= 3.10", "requests >= 2.32.5"],
)

from setuptools import setup, find_packages

setup(
    name="devguide",
    version="0.1.1",
    packages=find_packages(include=['devguide.*']),
    include_package_data=True,
    install_requires=[
        "scikit-learn>=1.2"
    ],
    entry_points={
        "console_scripts": [
            "devguide=devguide.cli:main"
        ]
    }
)

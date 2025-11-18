from setuptools import setup, find_packages

setup(
    name="devguide",
    version="0.2.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "scikit-learn==1.4.0",
        "rich",
        "appdirs",
        "stop-words"
    ],
    entry_points={
        "console_scripts": [
            "devguide=devguide.cli:main"
        ]
    }
)

from setuptools import setup, find_packages

setup(
    name="my-cli-app",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'my-cli-app = my_cli_app.__main__:main',
        ],
    },
)

from setuptools import setup

setup(
    name="task-manager",
    version="1.0.0",
    py_modules=["task_manager"],
    install_requires=[
        "click==8.1.7",
        "tabulate==0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "task=task_manager:cli",
        ],
    },
    author="Task Manager",
    description="A simple, powerful command-line task manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)

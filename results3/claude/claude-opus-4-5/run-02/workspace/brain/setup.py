from setuptools import setup

setup(
    name='brain',
    version='0.1.0',
    description='A terminal-based personal knowledge base',
    author='Claude',
    py_modules=['brain'],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'brain=brain:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)

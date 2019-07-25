from setuptools import setup

setup(
    name='uncompress',
    version='0.1',
    description='Tool for accessing zip/tar of compressed files.',
    url='http://github.com/StephanGocht/uncompress',
    author='Stephan Gocht',
    author_email='stephan@gobro.de',
    license='MIT',
    packages=['uncompress'],
    entry_points={
        'console_scripts': [
            'uncompress=uncompress:run_cmd_main',
        ]
    },
)

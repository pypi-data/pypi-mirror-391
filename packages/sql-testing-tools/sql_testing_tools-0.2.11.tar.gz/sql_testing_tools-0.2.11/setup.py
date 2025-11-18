from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    description = fh.read()


setup(
    name='sql_testing_tools',
    version='0.2.11',
    packages=find_packages(),
    install_requires=[
        'sqlparse>=0.5.1',
        'requests>=2.32.3'
    ],
    long_description=description,
    long_description_content_type="text/markdown"
)

from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ankillins",
    version="0.0.1",
    packages=find_namespace_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={
        'ankillins.templates': ['*.html'],
    },
    include_package_data=True,
    install_requires=[
        'colorama>=0.4.3',
        'click>=7.1.2',
        'requests>=2.24.0',
        'jsonschema>=3.2.0',
        'yarl>=1.4.2',
        'lxml>=4.5.2',
        'jinja2>=2.11.2',
        'tenacity>=6.2.0',
    ],
    entry_points={
        'console_scripts': [
            'ankillins= ankillins.cli:main'
        ]},
    author='Damir Chanyshev',
    author_email='hairygeek@yandex.com',
    description='Anki cards generating from CollinsDictionary pages',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='anki card generation collins',
    project_urls={
        "Bug Tracker": "https://github.com/hairygeek/ankillins",
        "Documentation": "https://github.com/hairygeek/ankillins",
        "Source Code": "https://github.com/hairygeek/ankillins",
    }
)

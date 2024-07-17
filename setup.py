from setuptools import setup, find_packages

# Function to read the version from a file
def get_version(rel_path):
    with open(rel_path, "r") as file:
        for line in file.readlines():
            if line.startswith('__version__'):
                # Grabs the first ' or " enclosed string
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

# Automatically load requirements from a requirements.txt file
def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Reading the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='DOLOST',
    version=get_version("src/DOLOST/version.py"),
    author_email="idi@base4sec.com",
    description="Deceptive Operations: Lure, Observe, and Secure Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Base4Security/DOLOS-T/",
    project_urls={
        "Bug Tracker": "https://github.com/Base4Security/DOLOS-T/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=load_requirements(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={
        'console_scripts': [
            'DOLOST = DOLOST.cli:main'
        ]
    },
)

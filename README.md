<p align="center">
	<a href="https://dolost.readthedocs.io/en/latest/" rel="noopener">
	 	<img src="https://github.com/dstainoB4/DOLOST/assets/103124157/2c478e1d-62a9-4b5c-8dca-68f2c77c9029" alt="DOLOST">
	</a>
</p>

<h3 align="center">DOLOST</h3>
<h4 align="center"><i>Deceptive Operations: Lure, Observe, and Secure Tool</i></h4>

<hr>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![PyPI version](https://badge.fury.io/py/dolost.svg)](https://badge.fury.io/py/dolost)
[![Documentation Status](https://readthedocs.org/projects/dolost/badge/?version=latest)](https://dolost.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-GPL-blue.svg)](/LICENSE)
[![DOI:10.13140/RG.2.2.34289.29289](https://img.shields.io/badge/DOI-10.13140/RG.2.2.34289.29289-0D72C2.svg)](https://doi.org/10.13140/RG.2.2.34289.29289)

</div>

<div align="center">

[![GitHub release](https://img.shields.io/github/release/Base4Security/DOLOS-T.svg)](https://GitHub.com/Base4Security/DOLOS-T/releases/)
[![GitHub issues](https://img.shields.io/github/issues/Base4Security/DOLOS-T.svg)](https://GitHub.com/Base4Security/DOLOS-T/issues/)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/Base4Security/DOLOS-T.svg)](https://GitHub.com/Base4Security/DOLOS-T/pull/)

</div>

## Table of Contents

- [About](#About)
- [Installation](#Installation)
- [Usage](#Usage)
- [Examples](/examples)
- [Contributing](/CONTRIBUTING.md)
- [License](/LICENSE.md)

## About

DOLOST is a framework designed to automate the creation and deployment of decoys and deceptive environments in the context of cyber deception operations.
It also guides the design of deception operations with a deep understanding of engagement strategies.

## Installation

1. **Ensure Python and Docker are Installed:**

   Make sure you have Python 3.7 or later installed on your system and Docker installed on your Decoy's host (it could be the same system you are using right now, just keep it in mind for when you configure DOLOST). You can download and install Python from the official Python website (https://www.python.org/downloads/) and Docker from the official Docker website (https://www.docker.com/get-started).

2. **Install DOLOST Using pip:**

   Run the following command to install the project:

	```bash
	# Python 3.7+ required
	$ python3 -m venv .venv
	$ source .venv/bin/activate
	$ pip install DOLOST
	```

3. **Final Checks:**

   Ensure that all required dependencies are installed without any errors. If you encounter any issues during the installation process, refer to the error messages for troubleshooting steps.


## Usage

To use the framework you need to start it with a first definition of the Docker client to connect with.

Here you have an example for DOLOST execution:

```python
import DOLOST

# Available Docker Client configuration:
# - from_env: Will try to use the current environment configuration to reach dockerd.
# - tcp: Will use the provided host and port to reach dockerd.
# - tcp_ssl: Will use the provided host and port + the SSL certificates to reach dockerd using TCP+SSL.
# - socket: Will use the provided socket path to reach dockerd.

# For more detailed information, refer to "Configuring Docker Client" in the Documentation.

dc = {'from_env': True}

# Available Verbosity Levels:
# - TRACE: Provides detailed tracing information.
# - DEBUG: Displays debug messages for troubleshooting.
# - INFO: Provides general information about the execution.
# - WARN: Displays warnings for potential issues.
# - ERROR: Indicates errors that occurred during execution.

# Note: Each verbosity level includes all levels above it. For example,
# setting verbosity to DEBUG will also display INFO, WARN, and ERROR messages.

verbosity = "INFO"
    
if __name__ == "__main__":
	DOLOST.start(verbosity=verbosity, docker_client=dc)
```

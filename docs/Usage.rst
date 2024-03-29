************************
Installation
************************

.. contents:: Table of Contents


Installing Requirements
=======================

Before you can use the project, you need to ensure that all required dependencies are installed and that you have a local copy of the project repository. Follow these steps to set up your environment:

1. **Ensure Python and Docker are installed:**

   Make sure you have Python 3.7 or later installed on your system and Docker installed on your Decoy's host (it could be the same system you are using right now, just keep it in mind for when you configure DOLOST). You can download and install Python from the official Python website (https://www.python.org/downloads/) and Docker from the official Docker website (https://www.docker.com/get-started).

2. **Install DOLOST Using pip:**

	.. note::
		You can create a virtual environment to avoid dependencies issues:

            .. code-block:: bash
        	   
               $ python3 -m venv venv

   Run the following command to install the project:

   .. code-block:: bash

      $ pip install DOLOST

3. **Final Checks:**

   Ensure that all required dependencies are installed without any errors. If you encounter any issues during the installation process, refer to the error messages for troubleshooting steps.

Once you've completed these steps, you'll have all the necessary dependencies installed, allowing you to use the project on your machine.


Developing
-----------------

If you wish to contribute to DOLOST, you can develop and share your modifications using the following environment.

1. **Clone the Project Repository:**

   Begin by cloning the project repository to your local machine. Open a terminal or command prompt and run the following command:

   .. code-block:: bash

      $ git clone https://github.com/Base4Security/DOLOS-T

2. **Navigate to Your Project Directory:**

   Once the repository is cloned, navigate to the directory where the project is located using the `cd` command:

   .. code-block:: bash

      $ cd DOLOST

3. **Ensure Python and Docker are installed:**

   Make sure you have Python 3.7 or later installed on your system and Docker installed on your Decoy's host (it could be the same system you are using right now, just keep it in mind for when you configure DOLOST). You can download and install Python from the official Python website (https://www.python.org/downloads/) and Docker from the official Docker website (https://www.docker.com/get-started).

4. **Install Dependencies Using pip:**

	.. note::
		You can create a virtual environment to avoid dependencies issues:

            .. code-block:: bash
               
               $ python3 -m venv venv

   Once you're in your project directory, run the following command to install the project's dependencies:

   .. code-block:: bash

      $ pip install -r requirements.txt

   This command reads the `requirements.txt` file in your project directory and installs all the necessary Python packages listed there.

5. **Final Checks:**

   Ensure that all required dependencies are installed without any errors. If you encounter any issues during the installation process, refer to the error messages for troubleshooting steps.


Initializing DOLOST
===================

Configuring Docker Client
--------------------------

Based on your desire and how you plan to implement DOLOST in your operation, you can configure the Decoy host to be on another server or simply configure it to connect in a specific way to the Docker API. This configuration would be based on how you configured your dockerd instance on the host to listen for the connection. 

For more information, you can refer to the official `Dockerd documentation <https://docs.docker.com/reference/cli/dockerd/>`_.

Also, you can configure the connection with the Docker client from the GUI! Check it out `here <#gui-modify-dclient>`_.

Using Docker Client Configuration from Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the Docker client to use settings from the environment, use the following:

.. note::
	The user that will run the framework, should have ``root`` access, be inside the ``docker`` group on UNIX or be able to interact with Docker's API.

.. code-block:: python

    import DOLOST

    # Connect to Docker environment using default settings
    dc = {'from_env': True}

    if __name__ == "__main__":
        # Start DOLOST with the desired verbosity level
        DOLOST.start(verbosity="INFO", docker_client=dc)

Using Docker over TCP
~~~~~~~~~~~~~~~~~~~~~~~

To configure the Docker client to connect over TCP, use the following:

.. code-block:: python

    import DOLOST

    # Connect to Docker over TCP without SSL
    dc = {'tcp': 'tcp://10.173.20.108:2375'}

    if __name__ == "__main__":
        # Start DOLOST with the desired verbosity level
        DOLOST.start(verbosity="INFO", docker_client=dc)

Using Docker over TCP with SSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the Docker client to connect over TCP with SSL, use the following:

.. code-block:: python

    import DOLOST

    # Connect to Docker over TCP with SSL
    dc = {
        'tcp_ssl': {
            'host': 'decoy-host.com',
            'port': 2376,
            'cert_path': '/path/to/cert.pem',
            'key_path': '/path/to/key.pem',
            'ca_path': '/path/to/ca.pem'
        }
    }

    if __name__ == "__main__":
        # Start DOLOST with the desired verbosity level
        DOLOST.start(verbosity="INFO", docker_client=dc)

Using Docker with Socket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the Docker client to connect using a unix/tcp/fd socket, use the following:

.. code-block:: python

    import DOLOST

    # Connect to Docker using a UNIX socket
    dc = {'socket': 'unix:///var/run/docker.sock'}

    if __name__ == "__main__":
        # Start DOLOST with the desired verbosity level
        DOLOST.start(verbosity="INFO", docker_client=dc)


Starting framework
--------------------

To use the framework, you need to start it with a first definition of the Docker env to connect with.

Here you have an example for DOLOST execution:

.. code-block:: python3
	
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




Debugging with Docker
======================

We utilize Docker environments as our deception field. Below are some useful commands to help you navigate and debug within the Docker environment:

List of Available Local Images
-------------------------------

To view the available local Docker images, use the following command:

.. code-block:: bash

    $ docker images

The images created by DOLOST will be created/stored within the repository ``DOLOST`` and the image tag will be the Decoy's name.

List Running Containers
----------------------------

To list all running containers within the Docker environment, execute the command:

.. code-block:: bash

    $ docker ps

The containers will be created using the following structure: ``DOLOST-SSH-DECOY`` or ``DOLOST-ApacheServer``.

Get Container Information
----------------------------

To obtain detailed information about a specific container, use:

.. code-block:: bash

    $ docker inspect %container%

Replace ``%container%`` with the container's ID or name.

Remove a Container
----------------------------

To remove a specific container from the Docker environment, execute:

.. code-block:: bash

    $ docker rm %container%

Replace ``%container%`` with the container's ID or name.

List Defined Networks
----------------------------

To list all defined networks within the Docker environment, use:

.. code-block:: bash

    $ docker network ls

Get Network Information
----------------------------

To retrieve detailed information about a specific network, execute:

.. code-block:: bash

    $ docker network inspect %network%

Replace ``%network%`` with the network's ID or name.

Remove a Network
----------------------------

To remove a specific network from the Docker environment, use:

.. code-block:: bash

    $ docker network rm %network%

Replace ``%network%`` with the network's ID or name.
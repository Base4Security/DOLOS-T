import os

class Context:
    """
    A class defining the context for the DOLOST application.

    Attributes:
        base_dir (str): The absolute path of the base directory.
        CONFIG_FOLDER (str): The folder name for Docker client configuration.
        CONFIG_FILE (str): The configuration file name.
        CONFIG_PATH (str): The absolute path to the configuration file.
    """
    # Define the base directory path as a class attribute
    base_dir = os.path.abspath(os.path.dirname(__file__))
    CONFIG_FOLDER = 'docker_client_config'
    CONFIG_FILE = 'config.json'
    CONFIG_PATH = os.path.abspath(os.path.join(CONFIG_FOLDER, CONFIG_FILE))
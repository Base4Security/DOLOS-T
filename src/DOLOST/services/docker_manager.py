import docker
import os, shutil, tempfile, ast, json
from .logger import DolostLogger
from ..context import Context

class DockerManager:
    """
    A class for managing the interactions with docker's API

    Attributes:
        _instance (cls): Instance of the class.
    """
    _instance = None

    @classmethod
    def get_instance(cls, docker_client=None):
        """
        Get an instance of the DockerManager class.

        If an instance does not exist, create a new one. If a `docker_client` is provided,
        configure the Docker client and check the connection.

        Args:
            docker_client (docker.client.DockerClient, optional): An instance of DockerClient to use for interaction.

        Returns:
            DockerManager: An instance of the DockerManager class.
        """
        if cls._instance is None:
            cls._instance = cls(docker_client=docker_client)
        
        elif docker_client is not None:
            cls._instance.configure_client(docker_client)
            cls._instance.check_connection()
        return cls._instance

    def __init__(self, docker_client=None):
        """
        Initialize a DockerManager instance.

        Args:
            docker_client: The way to connect to docker
        Returns:
            None
        """
        self.logger = DolostLogger.get_instance()
        self.client = None
        if docker_client:
            self.configure_client(docker_client)

    def check_connection(self):
        """
        Check if the Docker connection is successful.
        """
        if self.client is None:
            self.logger.error("[Docker] client is not set")

        try:
            self.client.ping()
            self.logger.debug("[Docker] connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Docker: {e}")
            return False

    def configure_client(self, docker_client=None):
        """
        Configure Docker client based on the provided configuration.

        Args:
            docker_client: Configuration for connecting to Docker client
        Returns:
            None
        """
        try:

            if 'from_env' in docker_client:
                self.client = docker.from_env()
                self.logger.trace("[Docker] client configured from ENV")

            elif 'tcp' in docker_client:
                self.client = docker.DockerClient(base_url=docker_client['tcp'])
                self.logger.trace("[Docker] client configured from TCP")

            elif 'ssl' in docker_client:
                tls_config = docker.tls.TLSConfig(
                    client_cert=(docker_client['tcp_ssl']['cert_path'], docker_client['tcp_ssl']['key_path']),
                    ca_cert=docker_client['tcp_ssl']['ca_path']
                )
                self.client = docker.DockerClient(base_url=f"tcp://{docker_client['tcp_ssl']['host']}:{docker_client['tcp_ssl']['port']}", tls=tls_config)
                self.logger.trace("[Docker] client configured from TCP+SSL")

            elif 'socket' in docker_client:
                self.client = docker.DockerClient(base_url=docker_client['socket'])
                self.logger.trace("[Docker] client configured from SOCKET")

            elif docker_client != None:
               # Check if the config folder and file exist
                self.logger.trace(f"[Docker] config file: {Context.CONFIG_PATH}")
                if os.path.exists(Context.CONFIG_PATH):
                    with open(Context.CONFIG_PATH, 'r') as config_file:
                        docker_client = json.load(config_file)
                        self.configure_client(docker_client=docker_client)
                        self.logger.trace("[Docker] client configuration loaded from config file")
                else:
                    self.logger.info("Config file not found. Using default configuration.")
                    docker_client = None
            else:
                raise ValueError("Invalid Docker client configuration")

            # Create the config folder if it doesn't exist
            if not os.path.exists(Context.CONFIG_FOLDER):
                os.makedirs(Context.CONFIG_FOLDER)

            # Write the docker_client data to config.json
            with open(Context.CONFIG_PATH, 'w') as config_file:
                json.dump(docker_client, config_file, indent=4)

        except Exception as e:
            self.logger.error(f"Failed to configure Docker client: {e}")
            self.client = None

    def check_client_configuration(self, docker_client):
        """
        Check before configuring Docker client based on the provided configuration.

        Args:
            docker_client: Configuration for connecting to Docker client
        Returns:
            None
        """
        try:
            if 'from_env' in docker_client:
                client = docker.from_env()
                self.logger.trace("Docker client configured from env")

            elif 'tcp' in docker_client:
                client = docker.DockerClient(base_url=docker_client['tcp'])
                self.logger.trace("Docker client configured from TCP")

            elif 'ssl' in docker_client:
                tls_config = docker.tls.TLSConfig(
                    client_cert=(docker_client['tcp_ssl']['cert_path'], docker_client['tcp_ssl']['key_path']),
                    ca_cert=docker_client['tcp_ssl']['ca_path']
                )
                client = docker.DockerClient(base_url=f"tcp://{docker_client['tcp_ssl']['host']}:{docker_client['tcp_ssl']['port']}", tls=tls_config)
                self.logger.trace("Docker client configured from TCP+SSL")

            elif 'socket' in docker_client:
                client = docker.DockerClient(base_url=docker_client['socket'])
                self.logger.trace("Docker client configured from SOCKET")

            else:
                raise ValueError("Invalid Docker client configuration")
                return False

            client.ping()
            self.logger.debug("Docker connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Docker client: {e}")
            return False

    def get_current_client_config(self):
        """
        Get the current Docker client configuration.

        Returns:
            dict or None: The current Docker client configuration loaded from the config file,
                          or None if the config file does not exist.
        """
        docker_client = None
        if os.path.exists(Context.CONFIG_PATH):
            with open(Context.CONFIG_PATH, 'r') as config_file:
                docker_client = json.load(config_file)
        return docker_client

    def build_context(self, source_service_folder, tmp_location, dockerfile_used):
        """
        Copy files to a temporary folder for Docker build context.

        Args:
            source_service_folder (str): Path to the source directory.
            tmp_location (str): Temporary directory to store the Docker build context.
            dockerfile_used (str): Path to the Dockerfile to be used.

        Returns:
            None
        """
        # Copy files to tmp folder
        tmp_app_destination = os.path.join(tmp_location, "app")

        # Verify if tmp location already exist
        if not os.path.exists(tmp_app_destination):
            os.makedirs(tmp_app_destination)

        # Copy service content to tmp_folder
        for item in os.listdir(source_service_folder):
            s = os.path.join(source_service_folder, item)
            d = os.path.join(tmp_app_destination, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        # Copy Dockerfile to tmp_folder
        tmp_dockerfile_destination = tmp_location + "/Dockerfile"
        shutil.copy(dockerfile_used, tmp_dockerfile_destination)

    def build_image(self, image_name=None, decoy_files=None, dockerfile_path=".",):
        """
        Build a Docker image based on the specified Dockerfile and service files.

        Args:
            image_name (str, optional): Name to tag the built image. If None, a default name will be used.
            decoy_files (str, optional): Path to the service files.
            dockerfile_path (str, optional): Path to the Dockerfile. Defaults to '.'.

        Returns:
            str: The image's id.
        """
        source_service_folder = os.path.join(Context.base_dir, f'decoyfiles/{decoy_files}')

        # Temp directory to copy to the Docker image
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            self.build_context(source_service_folder=source_service_folder, tmp_location=tmp_dir_name, dockerfile_used=dockerfile_path)

            if (image_name == "dolost-collector"):
                image_name = "collector_image:dolost"
            else:
                image_name = f"decoy_image_{decoy_files}:dolost"

            try:
                self.logger.info(f"Building Docker image '{image_name}'...")
                self.logger.trace(tmp_dir_name)


                build_output = self.client.api.build(
                    path=tmp_dir_name,
                    tag=image_name,
                    forcerm=True,
                    decode=True
                )
                # Iterate through the output and print progress
                for event in build_output:
                    if 'stream' in event:
                        lines = event['stream'].split('\n')
                        for line in lines:
                            if line.strip():
                                if "Step" in line.strip():
                                    self.logger.debug(line.strip())
                                else:
                                    self.logger.trace(line.strip())

                    if 'aux' in event and 'ID' in event['aux']:
                        image_id = event['aux']['ID']

                self.logger.info(f"Image '{image_name}' successfully built!")
                return image_name

            except docker.errors.BuildError as e:
                self.logger.error(f"Error building Docker image: {e}")

            except docker.errors.APIError as e:
                self.logger.error(f"Error accessing Docker API: {e}")

    def run_container(self, image_name, hostname, name, network_name=None, ipv4_address=None, subnet=None, gateway=None, ports=None ):
        """
        Run a Docker container based on the built image, with custom hostname and container name.

        Args:
            image_name (str): Name of the Docker image to run the container from.
            hostname (str): The container's decoy hostname.
            name (str): The container's name, used for management purposes.
            network_name (str, optional): The name of the network to connect the container to.
            ipv4_address (str, optional): The IPv4 address to assign to the container.
            subnet (str, optional): The subnet address to assign to the container's network.
            gateway (str, optional): The gateway IP address for the container's network.
            ports (dict): The ports configuration for mapping to containers.

        Returns:
            None
        """
        # Rename the name paramenter for the container
        name = f"DolosT-{name}"
        network_name =f"DolosT-{network_name}"
        
        # Check if the container already exist
        dolost_containers = self.get_containers()
        for dolost_container in dolost_containers:
             if name == dolost_container['Names'][0].lstrip('/'):
                self.logger.info(f"Container {name} already deployed. Skiping...")
                return
            
        if network_name:
            filters = {'name': [network_name]}
            network = self.client.api.networks(filters=filters)
            if network:
                self.logger.info(f"Network {network_name} already deployed. Skiping...")
            else:
                self.logger.info(f"Deploying network {network_name} ...")
                # Create the specified internal network if not already exists
                # Define the IPAM config, including the subnet
                ipam_pool = docker.types.IPAMPool(
                    subnet = subnet,
                    gateway = gateway
                )
                ipam_config = docker.types.IPAMConfig(
                    pool_configs=[ipam_pool]
                )
                # Not working BINDING + Internal or Host
                # If the network is not to the Collector leave it with internal access only
                #if (network_name == "DolosTCollectorNetwork"):
                #    NetworkDriver="bridge"
                #else:
                #    NetworkDriver="host"

                network = self.client.api.create_network(network_name, ipam=ipam_config)
                network_id = network["Id"]

        # Define extra_hosts for setting the gateway
        extra_hosts = {hostname: ipv4_address, "gateway": gateway} if network_name else None

        #Convert ports var from str to dict
        ports = ast.literal_eval(ports)  

        log_config = {
            "type": "syslog",
            "config": {
                "syslog-address": f"udp://200.100.0.247:514",
                # "syslog-format": "rfc5424", # Avoid sending the host's hostname
                "tag": hostname,
            }
        }

        # Defining log configuratión and port binding 
        host_config = self.client.api.create_host_config(
            log_config=log_config, 
            port_bindings=ports,
        )

        endpoint_config = self.client.api.create_endpoint_config(
            ipv4_address=ipv4_address,
            
        )
        
        networking_config = self.client.api.create_networking_config({
            network_name: endpoint_config,
        })
        # Continue with deploying the service without network
        container = self.client.api.create_container(
            image_name,
            detach=True,
            hostname=hostname,
            name=name,
            host_config=host_config,
            networking_config=networking_config
            # extra_hosts=extra_hosts,  # Pass extra_hosts here
        )

        #self.client.api.connect_container_to_network(
        #    container=container["Id"], 
        #    net_id=network_id,
        #    ipv4_address=ipv4_address,
        #)

        #Once we have the container, start it
        starting = self.client.api.start(container=container.get('Id'))

        self.logger.debug(f"Container ID: {container.get('Id')}")

    def start(self, container_id):
        """
        Starts a Docker container.

        Args:
            container_id (str): The ID of the container to start.

        Returns:
            None
        """
        try:
            self.client.api.start(container_id)
            self.logger.info(f"Container {container_id} started successfully.")
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to start container {container_id}: {e}")

    def stop(self, container_id):
        """
        Stops a Docker container.

        Args:
            container_id (str): The ID of the container to stop.

        Returns:
            None
        """
        try:
            self.client.api.stop(container_id)
            self.logger.info(f"Container {container_id} stopped successfully.")
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to stop container {container_id}: {e}")
    
    def clean_container(self, name):
        """
        Stop and remove a Docker container with the specified name.

        Args:
            name (str): The name of the Docker container to be cleaned.

        Returns:
            None
        """
        name = f"DolosT-{name}"    
        dolost_containers = self.get_containers()
        for container in dolost_containers:
            if name == container['Names'][0].lstrip('/'):
                self.logger.info(f"Cleaning Docker container '{name}'...")
                self.client.api.remove_container(container=name, force=True)
                self.logger.info(f"Container '{name}' successfully cleaned!")

    def clean_networks(self):
        """
        Remove unused Docker networks with the prefix DolosT-.

        Returns:
            None
        """
        network_name_prefix = "DolosT-"    
        dolost_networks = self.client.networks.list(names="DolosT-*")
        for network in dolost_networks:
            if network.containers == []:
                try:
                    self.client.api.remove_network(network.id)
                    self.logger.info("Network " + network.name + " successfully cleaned!")
                except:
                    self.logger.info("Network " + network.name + " cannot be cleaned, maybe its in use")

    def create_network(self, network_name, subnet, gateway):
        """
        Create a Docker network with the specified name, subnet, and gateway if it does not already exist.

        Args:
            network_name (str): The name of the network.
            subnet (str): The subnet in CIDR notation (e.g., '10.0.0.0/24').
            gateway (str): The gateway IP address for the network.

        Returns:
            None
        """
        try:
            networks = self.client.networks.get(network_name)
        except docker.errors.NotFound:
            ipam_pool = docker.types.IPAMPool(subnet=subnet, gateway=gateway)
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            self.client.networks.create(network_name, driver="bridge", ipam=ipam_config)

    def connect_to_network(self, container_name, network_name, ipv4_address, gateway):
        """
        Connect a Docker container to a network with the specified name, IP address, and gateway.

        Args:
            container_name (str): The name of the container to connect to the network.
            network_name (str): The name of the network.
            ipv4_address (str): The IPv4 address to assign to the container.
            gateway (str): The gateway IP address for the container's network.

        Returns:
            None
        """
        networks = self.client.networks.get(network_name)

        # Use extra_hosts to set the gateway
        extra_hosts = {container_name: ipv4_address, "gateway": gateway}

        networks.connect(container=container_name, ipv4_address=ipv4_address, extra_hosts=extra_hosts)

    def get_containers(self, all:bool=True):
        """
        Get the docker containers

        Args:
            all (bool): Retrieve all the containers, active or inactive ones.

        Returns:
            containers (list): The list of containers
        """
        return self.client.api.containers(all=all)

class ContainerStatsManager(DockerManager):
    """
    A class for managing container statistics retrieval and calculations.

    Inherits from DockerManager.

    Attributes:
        logger (DolostLogger, optional): The logger instance for logging messages.
        image_name (str, optional): The name of the Docker image.
        decoy_files (str, optional): The name of the service files directory.
        dockerfile_path (str, optional): The path to the Dockerfile.

    Methods:
        fetch_container_stats(container_id):
            Fetches stats for a specific container identified by its ID.

        calculate_cpu_percentage(precpu_stats, cpu_stats):
            Calculates the CPU usage percentage based on the provided CPU stats.

        calculate_memory_percentage(memory_stats):
            Calculates the memory usage percentage based on the provided memory stats.

        parse_container_stats(stats):
            Parses the raw container stats and returns a dictionary containing calculated statistics.
    """
    def __init__(self):
        """
        Initialize a ContainerStatsManager instance.

        Returns:
            None
        """
        docker_manager_instance = DockerManager.get_instance()
        self.logger = docker_manager_instance.logger
        self.client = docker_manager_instance.client

    def fetch_container_stats(self, container_id):
        """
        Fetches stats for a specific container identified by its ID.

        Args:
            container_id (str): The ID of the container.

        Returns:
            dict: A dictionary containing various container statistics.
        """
        stats = self.client.api.stats(container_id, stream=False)
        return self.parse_container_stats(stats)

    def calculate_cpu_percentage(self, precpu_stats, cpu_stats):
        """
        Calculates the CPU usage percentage based on the provided CPU stats.

        Args:
            precpu_stats (dict): The previous CPU stats.
            cpu_stats (dict): The current CPU stats.

        Returns:
            float: The CPU usage percentage.
        """
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
        system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
        number_cpus = cpu_stats['online_cpus']

        cpu_percentage = (cpu_delta / system_delta) * number_cpus * 100.0 if system_delta > 0 and cpu_delta > 0 else 0
        return cpu_percentage

    def calculate_memory_percentage(self, memory_stats):
        """
        Calculates the memory usage percentage based on the provided memory stats.

        Args:
            memory_stats (dict): The memory stats.

        Returns:
            float: The memory usage percentage.
        """
        memory_usage = memory_stats['usage']
        memory_limit = memory_stats['limit']

        memory_percentage = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0
        return memory_percentage

    def parse_container_stats(self, stats):
        """
        Parses the raw container stats and returns a dictionary containing calculated statistics.

        Args:
            stats (dict): The raw container stats.

        Returns:
            dict: A dictionary containing various container statistics.
        """
        cpu_percentage = self.calculate_cpu_percentage(stats['precpu_stats'], stats['cpu_stats'])
        memory_percentage = self.calculate_memory_percentage(stats['memory_stats'])

        network_rx = stats['networks']['eth0']['rx_bytes'] if 'networks' in stats else 0
        network_tx = stats['networks']['eth0']['tx_bytes'] if 'networks' in stats else 0

        disk_read, disk_write = 0, 0
        try:
            if 'blkio_stats' in stats and 'io_service_bytes_recursive' in stats['blkio_stats']:
                for stat in stats['blkio_stats']['io_service_bytes_recursive']:
                    if stat['op'] == 'Read':
                        disk_read += stat['value']
                    elif stat['op'] == 'Write':
                        disk_write += stat['value']
        except TypeError:
            pass

        return {
            'cpu_percentage': cpu_percentage,
            'memory_percentage': memory_percentage,
            'network_rx': network_rx,
            'network_tx': network_tx,
            # 'disk_read': disk_read,
            # 'disk_write': disk_write,
        }

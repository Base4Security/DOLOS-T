from flask import Blueprint, request, jsonify, Response, url_for
from functools import wraps
from ..services.docker_manager import DockerManager
from ..services.logger import DolostLogger
import os, json

from ..context import Context

# Construct the path to dockerfiles_templates
dockerfiles_path = os.path.join(Context.base_dir, 'dockerfiles_templates')

api_blueprint = Blueprint('api', __name__)

docker_manager = DockerManager.get_instance()
logger = DolostLogger.get_instance()

# Decorator for error handling
def error_handling(func):
    """
    Decorator for error handling.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapper function for error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error during operation: {str(e)}')
            raise
            return jsonify({"status": "error", "message": str(e)}), 500
    wrapper.__name__ = func.__name__
    return wrapper

# Load existing operations from the JSON file
def load_operations_db():
    """
    Load existing operations from the JSON file.

    Returns:
        list: A list containing operations data loaded from the JSON file.
    """
    try:
        with open('operationsdb.json', 'r') as f:
            operations = json.load(f)
    except FileNotFoundError:
        operations = []
    return operations

# Update the JSON file with modified operations data
def update_operations_db(data):
    """
    Update the JSON file with modified operations data.

    Args:
        data (list): The modified operations data to be written to the JSON file.
    """
    with open('operationsdb.json', 'w') as f:
        json.dump(data, f, indent=4)

# Update an operation based on it's ID
def update_operation_entry(operation_id, new_operation_content, update_decoys:bool=False):
    """
    Update an operation based on its ID.

    Args:
        operation_id (int): The ID of the operation to be updated.
        new_operation_content (dict): The new content for the operation.
        update_decoys (bool, optional): Whether to update decoys data. Defaults to False.
    """
    operations = load_operations_db()
    for operation in operations:
        if operation.get('id') == operation_id:
            # Update the operation content
            for key, value in new_operation_content.items():
                operation[key] = value
            # Update the decoys if update_decoys is True
            if update_decoys:
                operation['decoys'] = new_operation_content.get('decoys', operation.get('decoys', []))
            break
    update_operations_db(operations)

# Modify the operations's decoys 
def update_operation_decoys(operation_id, decoy):
    """
    Modify the operation's decoys.

    Args:
        operation_id (int): The ID of the operation.
        decoy (dict): Decoy information to be added to the operation.
    """
    operations_data = load_operations_db()

    operation = find_operation_by_id(operation_id)

    # Ensure that the "decoys" key holds a list
    if "decoys" not in operation or not isinstance(operation["decoys"], list):
        operation["decoys"] = []
    
    # Filter out any additional fields that are not needed for decoys
    required_decoy_keys = ["Hostname", "Description", "IP", "Subnet", "Gateway", "DeceptionNetwork", "ServicePorts", "Service", "DecoyFiles"]
    filtered_decoys = {key: decoy.get(key) for key in required_decoy_keys}

    # Append the new operation decoys
    operation["decoys"].append(filtered_decoys)
    
    # Write the updated decoys into the file
    return update_operation_entry(operation_id, operation, update_decoys=True)

# Generate ID for new operation based on the last ID in the JSON file
def generate_new_id(operations):
    """
    Generate ID for a new operation based on the last ID in the JSON file.

    Args:
        operations (list): List of existing operations.

    Returns:
        int: The ID for the new operation.
    """
    if not operations:
        return 1
    else:
        # We may need to implement a fail-safe approach
        return operations[-1]['id'] + 1

# Get operation from DB using id
def find_operation_by_id(operation_id):
    """
    Get an operation from the database using its ID.

    Args:
        operation_id (int): The ID of the operation to find.

    Returns:
        dict: The operation data if found, otherwise None.
    """
    operations = load_operations_db()
    for operation in operations:
        if operation.get('id') == operation_id:
            return operation
    return None  # Return None if no operation with the given id is found

# Create a new operation
@api_blueprint.route('/operations/new', methods=['POST'])
@error_handling
def new_operation():
    """
    Create a new operation.

    This endpoint allows the creation of a new operation. It expects a POST request with JSON data containing the necessary information for the new operation.

    Returns:
        jsonify: JSON response indicating the status of the operation creation.
            - status (str): Status of the operation creation ("OK" or "error").
            - message (str): Additional message providing details about the status.
            - redirect (str, optional): URL to redirect the client to upon successful operation creation.

    Raises:
        BadRequest: If the request data is invalid or missing required fields.
    """
    try:
        required_keys = {
            'preparation': ['name', 'objective', 'assets'],
            'narrative': ['storytelling', 'deception_activities', 'monitoring'],
            'closure_criteria': ['limits', 'end_date', 'commander'],
        }

        data = request.get_json()

        # Filter out any additional fields that are not in the required keys
        filtered_data = {}
        for section, keys in required_keys.items():
            if section in data:
                filtered_data[section] = {key: data[section][key] for key in keys if key in data[section]}
            else:
                filtered_data[section] = {}

        # Check if all required keys are present in the filtered data for each section
        missing_keys = []
        for section, keys in required_keys.items():
            missing_keys.extend([f"Missing key '{key}' in section '{section}'" for key in keys if key not in filtered_data[section]])

        if missing_keys:
            return jsonify({"status": "error", "message": "\n".join(missing_keys)}), 400

        # Check if the 'preparation' section is present and 'name' field is not empty
        if not filtered_data['preparation'].get('name'):
            return jsonify({"status": "error", "message": "The 'Operation Name' field under 'Preparation' section cannot be empty"}), 400

        # Check if decoys are provided and filter out any additional keys
        if 'decoys' in data:
            decoys = data['decoys']
            filtered_decoys = []
            for decoy in decoys:
                # Check if all required decoy keys are present
                required_decoy_keys = ["Hostname", "Description", "IP", "Subnet", "Gateway", "DeceptionNetwork", "ServicePorts", "Service", "DecoyFiles"]
                missing_decoy_keys = [key for key in required_decoy_keys if key not in decoy]
                if missing_decoy_keys:
                    return jsonify({"status": "error", "message": f"Missing key(s) {', '.join(missing_decoy_keys)} in decoy"}), 400
                filtered_decoys.append({key: decoy[key] for key in required_decoy_keys})
            filtered_data['decoys'] = filtered_decoys

        new_operation = filtered_data
        actual_operations = load_operations_db()
        
        # Generate ID for the new operation
        new_id = generate_new_id(actual_operations)
        
        # Add the new operation data to the list with the generated ID
        new_operation['id'] = new_id
        actual_operations.append(new_operation)
        update_operations_db(actual_operations)
        
        return jsonify({"status": "OK", "redirect": url_for('views.view_operation', operation_id=new_id)})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Edit an operation
@api_blueprint.route('/operations/<int:operation_id>/edit', methods=['POST'])
@error_handling
def edit_operation(operation_id):
    """
    Edit an existing operation.

    Args:
        operation_id (int): The ID of the operation to edit.

    Returns:
        jsonify: JSON response indicating the status of the operation editing.
    """
    try:
        required_keys = {
            'preparation': ['name', 'objective', 'assets'],
            'narrative': ['storytelling', 'deception_activities', 'monitoring'],
            'closure_criteria': ['limits', 'end_date', 'commander'],
        }

        data = request.get_json()

        # Filter out any additional fields that are not in the required keys
        filtered_data = {}
        for section, keys in required_keys.items():
            if section in data:
                filtered_data[section] = {key: data[section][key] for key in keys if key in data[section]}
            else:
                filtered_data[section] = {}

        # Check if all required keys are present in the filtered data for each section
        missing_keys = []
        for section, keys in required_keys.items():
            missing_keys.extend([f"Missing key '{key}' in section '{section}'" for key in keys if key not in filtered_data[section]])

        if missing_keys:
            return jsonify({"status": "error", "message": "\n".join(missing_keys)}), 400

        # Check if the 'preparation' section is present and 'name' field is not empty
        if not filtered_data['preparation'].get('name'):
            return jsonify({"status": "error", "message": "The 'Operation Name' field under 'Preparation' section cannot be empty"}), 400

        edited_operation_data = filtered_data

        update_operation_entry(operation_id, edited_operation_data, update_decoys=False)
        
        return jsonify({"status": "OK", "redirect": url_for('views.view_operation', operation_id=operation_id)})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Remove operation
@api_blueprint.route('/operations/remove/<string:operation_id>', methods=['DELETE'])
@error_handling
def remove_operation(operation_id):
    """
    Remove an operation.

    Args:
        operation_id (str): The ID of the operation to remove.

    Returns:
        jsonify: JSON response indicating the status of the operation removal.
    """
    try:
        operations_data = load_operations_db()

        # Find the operation by ID
        operation_to_remove = find_operation_by_id(int(operation_id))
        if operation_to_remove:
            # Delete the operation data
            operations_data.remove(operation_to_remove)

            update_operations_db(operations_data)

            return jsonify({'message': f'We removed the operation {operation_id}'}), 202
        else:
            return jsonify({'message': f'Operation {operation_id} not found'}), 404

    except Exception:
        return jsonify({'message': f'We can not remove operation {operation_id}'}), 406

# Create a new decoy
@api_blueprint.route('/operations/<int:operation_id>/decoy/new', methods=['POST'])
@error_handling
def new_decoy(operation_id):
    """
    Create a new decoy for an operation.

    Args:
        operation_id (int): The ID of the operation to add the decoy to.

    Returns:
        jsonify: JSON response indicating the status of the new decoy creation.
    """
    data = request.get_json()
    update_operation_decoys(operation_id, data)

    return jsonify({"status": "OK", "message": "New decoy saved"}), 200
      
# Helper function for deployment logic
def deploy_service(image_name, dockerfile_path, decoy_files, service_info):
    """
    Deploy a service using Docker.

    Args:
        image_name (str): The name of the Docker image.
        dockerfile_path (str): The path to the Dockerfile.
        decoy_files (str): The path to service files.
        service_info (dict): Information about the service.

    Returns:
        None
    """
    image_name = docker_manager.build_image(image_name=image_name, decoy_files=decoy_files, dockerfile_path=dockerfile_path)
    docker_manager.run_container(image_name=image_name,**service_info)
    logger.info(f"Deployed container: {service_info['hostname']}")

# Fetch current available Dockerfiles
def get_supported_services():
    """
    Fetches the current available Dockerfile services.

    Returns:
        list: A list of supported services.
    """
    supported_services = []

    for filename in os.listdir(dockerfiles_path):
        if filename.startswith("Dockerfile-"):
            service_name = filename.replace("Dockerfile-", "")
            supported_services.append(service_name)

    return supported_services

@api_blueprint.route('/deploy', methods=['POST'])
@error_handling
def deploy_env():
    """
    Endpoint for deploying the environment.

    Returns:
        Response: A response indicating the deployment status.
    """
    data = request.get_json()
    deploy_collector()
    for decoy in data:
        deploy_decoy(decoy)
    
    return Response("Env Deployed", mimetype='text/plain')

def deploy_collector():
    """
    Deploy the collector service.

    Returns:
        None
    """
    service_dockerfile_path = os.path.join(dockerfiles_path, 'Dockerfile-collector')
    if not os.path.exists(service_dockerfile_path):
        logger.error('Dockerfile not found for Collector')
        return
    
    collector_info = {
        "hostname": "Collector",
        "name": "Collector",
        "network_name": "CollectorNetwork",
        "ipv4_address": "200.100.0.247",
        "subnet": "200.100.0.0/24",
        "gateway": "200.100.0.1",
        "ports": "{'514/tcp': 524, '514/udp': 524 }"
    }
    
    deploy_service(
        image_name="dolost-collector",
        dockerfile_path=service_dockerfile_path,
        decoy_files="collector",
        service_info=collector_info
    )

def deploy_decoy(decoy):
    """
    Deploy a decoy service.

    Args:
        decoy (dict): Decoy information including hostname, network settings, and service details.

    Returns:
        None
    """
    deploy_collector()
    supported_services = get_supported_services()
    decoyservice = decoy["Service"].lower()
    
    if decoyservice not in supported_services:
        logger.error(f"We do not yet offer the service: {decoyservice}")
        return

    decoy_info = {
        "hostname": decoy["Hostname"],
        "name": decoy["Hostname"],
        "network_name": decoy["DeceptionNetwork"],
        "ipv4_address": decoy["IP"],
        "subnet": decoy["Subnet"],
        "gateway": decoy["Gateway"],
        "ports": decoy["ServicePorts"]
    }
    dockerfile_path = os.path.join(dockerfiles_path, f'Dockerfile-{decoyservice}')

    deploy_service(
        image_name=decoyservice,
        dockerfile_path=dockerfile_path,
        decoy_files=decoy["DecoyFiles"],
        service_info=decoy_info
    )

# Remove deployed decoys
@api_blueprint.route('/decoys/clean', methods=['POST'])
@error_handling
def clean_env():
    """
    Endpoint to remove deployed decoys.

    Returns:
        Response: Response indicating the success of the operation.
    """
    # PENDING search for dolost tag
    data = request.get_json()
    for decoy in data:
        clean_decoy(decoy)
    logger.info(f"Removed decoys")
    return Response("Decoys cleaned", mimetype='text/plain')

# Remove decoy
def clean_decoy(decoy):
    """
    Remove decoy.

    Args:
        decoy (dict): Decoy information.

    Returns:
        Response: Response indicating the success of the operation.
    """

    decoy_to_clean = decoy["Hostname"]
    docker_manager.clean_container(decoy_to_clean)

    return Response("A decoy was cleaned", mimetype='text/plain')

# Remove collector
@api_blueprint.route('/collector/clean', methods=['POST'])
@error_handling
def clean_collector():
    """
    Remove collector.

    Returns:
        Response: Response indicating the success of the operation.
    """
    collector_to_clean = "Collector"
    docker_manager.clean_container(collector_to_clean)
    logger.info(f"Removed Collector")
    return Response("Collector cleaned", mimetype='text/plain')

# Remove networks
@api_blueprint.route('/networks/clean', methods=['POST'])
@error_handling
def clean_networks():
    """
    Remove networks.

    Returns:
        Response: Response indicating the success of the operation.
    """
    docker_manager.clean_networks()
    logger.info(f"Removed Networks")
    return Response("Networks cleaned", mimetype='text/plain')

# Start an specific decoy
@api_blueprint.route('/decoys/start', methods=['POST'])
@error_handling
def decoys_start():
    """
    Start a specific decoy.

    Returns:
        Response: JSON response indicating the status of the operation.
    """
    try:
        data = request.get_json()

        docker_manager.start(container_id=data['containerId'])

        return jsonify({"status": "OK", "message": "The container has been started successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Stop an specific decoy
@api_blueprint.route('/decoys/stop', methods=['POST'])
@error_handling
def decoys_stop():
    """
    Stop a specific decoy.

    Returns:
        Response: JSON response indicating the status of the operation.
    """

    try:
        data = request.get_json()

        docker_manager.stop(container_id=data['containerId'])

        return jsonify({"status": "OK", "message": "The container has been stopped successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Deploy an specific decoy, including building and deployment
@api_blueprint.route('/operations/<int:operation_id>/decoys/deploy', methods=['POST'])
@error_handling
def deploy_container(operation_id):
    """
    Deploy a specific decoy, including building and deployment.

    Args:
        operation_id (int): The ID of the operation associated with the decoy.

    Returns:
        Response: JSON response indicating the status of the operation.
    """
    try:
        data = request.get_json()

        operation_data = find_operation_by_id(operation_id)

        decoy_data = None

        for decoy in operation_data.get('decoys', []):
            if "DolosT-" + decoy.get('Hostname') ==  data.get('containerHostname'):
                decoy_data = decoy
                break

        if decoy_data:
            deploy_decoy(decoy_data)
            return jsonify({"status": "OK", "message": "The container has been deployed successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Decoy not found on stored decoys"}), 404

    except Exception as e:
        logger.error(f"Error deploying container: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Undeploy an specific container decoy
@api_blueprint.route('/operations/<int:operation_id>/decoys/undeploy', methods=['DELETE'])
@error_handling
def undeploy_container(operation_id):
    """
    Undeploy a container decoy for an operation.

    Args:
        operation_id (int): The ID of the operation containing the decoy.

    Returns:
        jsonify: JSON response indicating the status of the container undeployment.
    """
    try:
        data = request.get_json()

        operation_data = find_operation_by_id(operation_id)

        decoy_data = None

        for decoy in operation_data.get('decoys', []):
            if "DolosT-" + decoy.get('Hostname') ==  data.get('containerHostname'):
                decoy_data = decoy
                break

        if decoy_data:
            clean_decoy(decoy_data)
            return jsonify({"status": "OK", "message": "The container has been undeployed successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Decoy not found on stored decoys"}), 404

    except Exception as e:
        logger.error(f"Error undeploying container: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Delete an specific decoy
@api_blueprint.route('/operations/<int:operation_id>/decoys/delete', methods=['DELETE'])
@error_handling
def delete_decoy(operation_id):
    """
    Delete a specific decoy from an operation.

    Args:
        operation_id (int): The ID of the operation containing the decoy.

    Returns:
        jsonify: JSON response indicating the status of the decoy deletion.
    """
    try:
        data = request.get_json()
        decoy_to_delete = data["decoyHostname"]
        decoy_to_delete = decoy_to_delete.replace("DolosT-", "")
        operation = find_operation_by_id(operation_id)

        operation['decoys'] = [decoy for decoy in operation['decoys'] if decoy["Hostname"] != decoy_to_delete]

        print(operation)

        update_operation_entry(operation_id, operation, update_decoys=True)

        
        return jsonify({"status": "OK", "message": "The decoy has been deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting decoy: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/config/docker_client', methods=['POST'])
@error_handling
def modify_docker_client():
    """
    Modify the Docker client configuration.

    Returns:
        jsonify: JSON response indicating the status of the Docker client configuration modification.
    """
    def save_file(file_path, content):
        with open(file_path, 'w') as f:
            f.write(content)

    # Check if the folder exists, if not, create it
    if not os.path.exists(Context.CONFIG_FOLDER):
        os.makedirs(Context.CONFIG_FOLDER)

    data = request.get_json()
    
    # Extract data from JSON payload
    config_type = data.get('type')

    dc = {}

    if config_type == "env":
        dc = {'from_env': True}

    elif config_type == "tcp":
        host = data.get('host')
        port = data.get('port')
        dc =  {'tcp': f"tcp://{host}:{port}"}

    elif config_type == "socket":
        socketPath = data.get('socketPath')
        dc = {'socket': socketPath}

    elif config_type == 'tcp_ssl':
        host = data.get('host')
        port = data.get('port')
        ssl_cert = data.get('sslCert')
        ssl_key = data.get('sslKey')
        ssl_ca = data.get('sslCa')
        save_file(os.path.join(Context.CONFIG_FOLDER, 'ssl_cert.pem'), ssl_cert)
        save_file(os.path.join(Context.CONFIG_FOLDER, 'ssl_key.pem'), ssl_key)
        save_file(os.path.join(Context.CONFIG_FOLDER, 'ssl_ca.pem'), ssl_ca)
        dc['tcp_ssl'] = {
            'host': host,
            'port': port,
            'cert_path': os.path.join(Context.CONFIG_FOLDER, 'ssl_cert.pem'),
            'key_path': os.path.join(Context.CONFIG_FOLDER, 'ssl_key.pem'),
            'ca_path': os.path.join(Context.CONFIG_FOLDER, 'ssl_ca.pem')
        }
    else:
        return jsonify({"status": "error", "message": "Invalid configuration sent"}), 400

    try:
        status = docker_manager.check_client_configuration(docker_client=dc)
        if status:        
            docker_manager.configure_client(docker_client=dc)
            docker_manager.check_connection()
            return jsonify({"status": "OK", "message": "Docker client updated successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Could not connect to docker client"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

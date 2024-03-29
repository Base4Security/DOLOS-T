from flask import Blueprint, jsonify, render_template, request
from .api import load_operations_db, find_operation_by_id
from ..services.docker_manager import DockerManager
from ..services.logger import DolostLogger
import json
import os


views_blueprint = Blueprint('views', __name__)

logger = DolostLogger.get_instance()
docker_manager = DockerManager.get_instance()

## Frontend Interactions

# Activity view
@views_blueprint.route('/')
@views_blueprint.route('/activity')
def activity():
    """
    Render the activity view.

    Returns:
        str: Rendered HTML template for the activity view.
    """
    return render_template('view_activity.html')

# Operations dashboard
@views_blueprint.route('/operations')
def operations():
    """
    Render the operations dashboard.

    Returns:
        str: Rendered HTML template containing the operations dashboard.
    """
    operations_data = load_operations_db()
    return render_template('operations.html', data=operations_data)

# Endpoint to view operation by ID
@views_blueprint.route('/operations/view/<int:operation_id>', methods=['GET'])
def view_operation(operation_id):
    """
    View details of a specific operation by ID.

    Args:
        operation_id (int): The ID of the operation to view.

    Returns:
        str: Rendered HTML template containing the details of the specified operation.
    """
    try:
        operation = find_operation_by_id(operation_id)

        if operation:
            operation_decoys = operation["decoys"]
            all_containers = docker_manager.get_containers(all=True)
            decoy_names = [entry['Hostname'] for entry in operation_decoys]
            logger.debug(f"Operation's decoy names:  {decoy_names}", ws=False)

            # Create a list to hold all decoys
            operation_decoys_processed = []

            # Process each decoy, check if it's deployed, and format the data
            for decoy in operation_decoys:
                deployed = False
                decoy_data = {
                    'Hostname': f"DolosT-{decoy['Hostname']}",
                    'Description': decoy['Description'],
                    'IP': decoy['IP'],
                    'Subnet': decoy['Subnet'],
                    'Gateway': decoy['Gateway'],
                    'DeceptionNetwork': decoy['DeceptionNetwork'],
                    'ServicePorts': decoy['ServicePorts'],
                    'Service': decoy['Service'],
                    'DecoyFiles': decoy['DecoyFiles'],
                }

                # Check if the decoy has a corresponding container
                for container in all_containers:
                    if f"/DolosT-{decoy['Hostname']}" in container.get('Names', []):
                        deployed = True
                        # Modify the showed stats, from the .json's data to active docker data
                        decoy_data['Id'] = container['Id']
                        decoy_data['Status'] = container['Status']
                        docker_network = "DolosT-" + decoy['DeceptionNetwork']
                        ip_address = container['NetworkSettings']['Networks'][docker_network]['IPAddress']
                        subnet = container['NetworkSettings']['Networks'][docker_network]['IPAddress']
                        netmask = container['NetworkSettings']['Networks'][docker_network]['IPPrefixLen']
                        gateway = container['NetworkSettings']['Networks'][docker_network]['Gateway']
                        
                        decoy_data['IP'] = ip_address if ip_address != "" else "N/A"
                        decoy_data['Subnet'] = f'{subnet}/{netmask}' if subnet != "" else "N/A"
                        decoy_data['Gateway'] = gateway if gateway != "" else "N/A"
                        break

                # If not deployed, set default status and network settings
                if not deployed:
                    decoy_data['Status'] = 'Not Deployed'

                # Add processed decoy data to the list
                operation_decoys_processed.append(decoy_data)

            # Pass the processed decoys to the template
            return render_template('view_operation.html', operation=operation, containers=operation_decoys_processed)
        else:
            return jsonify({'error': 'Operation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Docker client config view
@views_blueprint.route('/config/docker_client')
def docker_client_config():
    """
    Render the Docker client configuration view.

    Returns:
        str: Rendered HTML template for the Docker client configuration view.
    """
    return render_template('docker_client_config.html', docker_config=docker_manager.get_current_client_config())
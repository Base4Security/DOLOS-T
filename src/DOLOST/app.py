from flask import Flask
from flask_socketio import SocketIO
from .services.docker_manager import DockerManager
from .services.logger import DolostLogger
from .blueprints.api import api_blueprint
from .blueprints.views import views_blueprint
from .blueprints.websocket import WebSocketNamespace
from .context import Context

def main(verbosity="INFO", docker_client=None, host="127.0.0.1", port:int=9874):
    """
    Main function to start the DOLOST application.

    Args:
        verbosity (str, optional): Verbosity level for logging (default is "INFO").
        docker_client (dict, optional): Configuration for connecting to the Docker client.
        host (str, optional): The host IP address to run the application (default is "127.0.0.1").
        port (int, optional): The port number to run the application (default is 9874).

    Returns:
        None
    """
    app = Flask(__name__)

    production = False
    if production:
        async_mode = 'gevent'
        debug = False
    else:
        async_mode = 'threading'
        debug = True

    socketio = SocketIO(app, async_mode=async_mode)

    # Register Blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api/')
    app.register_blueprint(views_blueprint)

    # Register the WebSocket namespace
    socketio.on_namespace(WebSocketNamespace('/'))

    # Initialize singletons or services
    logger_service = DolostLogger.get_instance(socketio=socketio, level=verbosity)
    docker_manager_service = DockerManager.get_instance(docker_client=docker_client)

    socketio.run(app, debug=debug, host=host, port=port)
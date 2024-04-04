from flask_socketio import Namespace, emit
from ..services.logger import DolostLogger
from ..services.docker_manager import ContainerStatsManager
from ..services.activity import ActivityViewer
import threading

class WebSocketNamespace(Namespace):
    """Namespace for WebSocket connections."""

    def __init__(self, namespace=None):
        """
        Initialize the WebSocketNamespace.

        :param str namespace: The namespace for the WebSocket.

        """
        super().__init__(namespace)
        self.logger = DolostLogger.get_instance()
        self.activity_logs_thread = None
        self.thread_stop_event = threading.Event()  # Event to signal thread termination

    def on_connect(self, *args):
        """
        Callback function triggered when a client connects.

        :param \*args: Variable length argument list.

        """
        self.logger.trace("[WS] Client connected", ws=False)
        emit('heartbeat', {'data': 'Connected'})

    def on_disconnect(self, *args):
        """
        Callback function triggered when a client disconnects.

        :param \*args: Variable length argument list.

        """
        self.logger.trace("[WS] Client disconnected", ws=False)
        if self.activity_logs_thread:
            self.thread_stop_event.set()

    def on_request_data(self, json_data):
        """
        Callback function triggered on request for data.

        :param dict json_data: JSON object containing the request data.
            Should contain 'container_id' key.

        """
        if 'container_id' in json_data and isinstance(json_data['container_id'], str):
            container_id = json_data['container_id']
            data = ContainerStatsManager().fetch_container_stats(container_id)
            emit('update_data', data)
        else:
            emit('update_data_error', {'error': 'Invalid or missing container_id'})

    def send_activity_logs(self):
        """
        Send activity logs to clients.

        Continuously fetches and emits activity logs until stop event is set.

        """
        while not self.thread_stop_event.is_set():
            logs = ActivityViewer.review_logs()
            self.emit('activity_logs', {'logs': logs})

            observable_ips = ActivityViewer.review_observable_ips()
            self.emit('activity_observable_ips', {'observable_ips': observable_ips})

            observable_usage = ActivityViewer.review_observable_usage()
            self.emit('activity_observable_usage', {'observable_usage': observable_usage})

            observable_interesting = ActivityViewer.review_interesting_observable()
            self.emit('activity_observable_interesting', {'observable_interesting': observable_interesting})

            self.thread_stop_event.wait(5)  # Wait for 5 second before sending next update

    def on_request_activity(self):
        """
        Callback function triggered on request for activity logs.

        Starts a new thread to continuously send activity logs to clients.

        """
        if not self.activity_logs_thread or not self.activity_logs_thread.is_alive():
            # Start a new thread only if it's not already running
            self.thread_stop_event.clear()  # Clear the event flag
            self.activity_logs_thread = threading.Thread(target=self.send_activity_logs)
            self.activity_logs_thread.start()

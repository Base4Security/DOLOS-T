import logging
from datetime import datetime
from flask_socketio import SocketIO


class DolostLogger:
	"""
	DolostLogger class provides a simple interface for logging messages with custom log levels
	and emitting those messages to a Socket.IO instance.

	Attributes:
		TRACE (int): Custom log level representing trace messages.
		DEBUG (int): Standard logging.DEBUG level.
		INFO (int): Standard logging.INFO level.
		WARN (int): Custom log level representing warning messages.
		ERROR (int): Standard logging.ERROR level.
		_instance (cls): Instance of the class.

	Methods:
		__init__(self, socketio, level=logging.INFO):
			Initializes a DolostLogger instance.

		_get_numeric_level(self, level):
			Convert a log level from its string representation to the corresponding numeric value.
		
		_register_custom_levels(self):
			Register custom log levels (TRACE and WARN) with the logging module.
		
		_format_log(self, level, message):
			Colorize the log level and message using ANSI escape codes.

		emit_socketio_message(self, message, verbose='INFO'):
			Emits a message to a Socket.IO instance with a specified verbosity level.

		log(self, message, level=logging.INFO):
			Logs a message with a specified log level and emits it to a Socket.IO instance.

		trace(self, message, ws=True):
			Logs a message with the TRACE log level and emits it to a Socket.IO instance.

		debug(self, message, ws=True):
			Logs a message with the DEBUG log level and emits it to a Socket.IO instance.

		info(self, message, ws=True):
			Logs a message with the INFO log level and emits it to a Socket.IO instance.

		warn(self, message, ws=True):
			Logs a message with the WARN log level and emits it to a Socket.IO instance.

		error(self, message, ws=True):
			Logs a message with the ERROR log level and emits it to a Socket.IO instance.
	"""
	TRACE = 5
	DEBUG = logging.DEBUG
	INFO = logging.INFO
	WARN = 35
	ERROR = logging.ERROR
	_instance = None

	@classmethod
	def get_instance(cls, socketio=None, level="TRACE"):
		"""
		Returns the instance of DolostLogger, creating it if necessary.

		Args:
			socketio (Socket.IO): An instance of the Socket.IO class.
			level (str): The log level. Defaults to 'TRACE'.

		Returns:
			DolostLogger: An instance of DolostLogger.

		"""
		if cls._instance is None:
			cls._instance = cls(socketio=socketio, level=level)

		elif socketio is not None:
			cls._instance.socketio = socketio
			cls._instance.logger.setLevel(level)

		return cls._instance

	def __init__(self, socketio: SocketIO, level=logging.INFO):
		"""
		Initializes a DolostLogger instance.

		Args:
			socketio: A Socket.IO instance for emitting messages.
			level (int): The default log level for console prints. Defaults to logging.INFO.
		"""
		self._register_custom_levels()
		self.socketio = socketio
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.TRACE)

		# Set up a console logger with the specified default level
		console_handler = logging.StreamHandler()
		console_handler.setLevel(self._get_numeric_level(level))

		# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

		# console_handler.setFormatter(formatter)
		self.logger.addHandler(console_handler)

	def _get_numeric_level(self, level):
		"""
		Convert a log level from its string representation to the corresponding numeric value.

		Args:
			level (str or int): The log level, either as a string or numeric value.

		Returns:
			int: The numeric representation of the log level.
		"""
		if isinstance(level, str):
			level = getattr(self, level.upper(), logging.INFO)
		return level

	def _register_custom_levels(self):
		"""
		Register custom log levels (TRACE and WARN) with the logging module.

		Returns:
			None
		"""
		# Register custom log levels
		logging.addLevelName(self.TRACE, 'TRACE')
		setattr(logging, 'TRACE', self.TRACE)

		logging.addLevelName(self.WARN, 'WARN')
		setattr(logging, 'WARN', self.WARN)

		logging.getLogger().setLevel(self.TRACE)
		logging.getLogger().setLevel(self.WARN)

	def _format_log(self, level, message):
		"""
		Colorize the log level and message using ANSI escape codes.

		Args:
			level (str): The log level.
			message (str): The log message.

		Returns:
			str: The colorized log level and message.
		"""
		current_time = datetime.now().strftime('%b %d %H:%M:%S')

		# Map log levels to ANSI color codes
		color_mapping = {
			'TRACE': '\033[1;95m',  # COLOR_MAGENTA
			'DEBUG': '\033[1;92m',  # COLOR_CYAN
			'INFO':  '\033[1;96m',  # COLOR_LIGHT_GREEN
			'WARN':  '\033[1;93m',  # COLOR_YELLOW
			'ERROR': '\033[1;91m',  # COLOR_RED
		}
		COLOR_RESET = '\033[0m'

		return f"{color_mapping.get(level, '')}[{level}] {current_time} :: {message}{COLOR_RESET}"

	def emit_socketio_message(self, message, verbose='INFO'):
		"""
		Emits a message to a Socket.IO instance with a specified verbosity level.

		Args:
			message (str): The message to emit.
			verbose (str): The verbosity level for the message. Defaults to 'INFO'.
		"""
		if self.socketio is not None:
			self.socketio.emit('docker_status', {'message': message, 'verbose': verbose})
		else:
			# Log an error or warning that socketio is not initialized
			print("Attempted to emit a socketio message before socketio was initialized")

	def log(self, message, ws:bool, level=logging.INFO):
		"""
		Logs a message with a specified log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			level (int): The log level. Defaults to logging.INFO.
			ws (bool): Emit the message over WebSockets.
		"""
		level_str = logging.getLevelName(level)
		colored_message = self._format_log(level_str, message)
		self.logger.log(level, colored_message)
		if ws:
			self.emit_socketio_message(message, verbose=level_str)

	def trace(self, message, ws=True):
		"""
		Logs a message with the TRACE log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			ws (bool): Emit the message over WebSockets. Defaults to True.
		"""
		self.log(message, level=self.TRACE, ws=ws)

	def debug(self, message, ws=True):
		"""
		Logs a message with the DEBUG log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			ws (bool): Emit the message over WebSockets. Defaults to True.
		"""
		self.log(message, level=self.DEBUG, ws=ws)

	def info(self, message, ws=True):
		"""
		Logs a message with the INFO log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			ws (bool): Emit the message over WebSockets. Defaults to True.
		"""
		self.log(message, level=self.INFO, ws=ws)

	def warn(self, message, ws=True):
		"""
		Logs a message with the WARN log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			ws (bool): Emit the message over WebSockets. Defaults to True.
		"""
		self.log(message, level=self.WARN, ws=ws)

	def error(self, message, ws=True):
		"""
		Logs a message with the ERROR log level and emits it to a Socket.IO instance.

		Args:
			message (str): The message to log and emit.
			ws (bool): Emit the message over WebSockets. Defaults to True.
		"""
		self.log(message, level=self.ERROR, ws=ws)
CLI
====

You can use DOLOST directly from the CLI.

If you want to initiate the framework, you can do it using the following arguments.

Command-line Arguments
----------------------

.. csv-table::
   :header: "Argument", "Description", "Default Value"

   "``--host``, ``-H``", "Host to run the server on", "'127.0.0.1'"
   "``--port``, ``-p``", "Port to run the server on", "9874"
   "``--verbosity``, ``-v``", "Verbosity level ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR')", "'INFO'"
   "``--docker-client``, ``-dc``", "Docker client type ('tcp', 'tcp_ssl', 'socket', 'env')", "'env'"

TCP options
~~~~~~~~~~~~

.. csv-table::
   :header: "Argument", "Description", "Default Value"

   "``--tcp-host``", "Host for TCP connection (required for ``--docker-client`` tcp)", ""
   "``--tcp-port``", "Port for TCP connection (required for ``--docker-client`` tcp)", ""

TCP+SSL options
~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Argument", "Description", "Default Value"

   "``--ssl-host``", "Host for TCP+SSL connection (required for ``--docker-client`` tcp_ssl)", ""
   "``--ssl-port``", "Port for TCP+SSL connection (required for ``--docker-client`` tcp_ssl)", ""
   "``--ssl-cert``", "Path to client certificate (required for ``--docker-client`` tcp_ssl)", "'cert.pem'"
   "``--ssl-key``", "Path to client key (required for ``--docker-client`` tcp_ssl)", "'key.pem'"
   "``--ssl-ca``", "Path to CA certificate (required for ``--docker-client`` tcp_ssl)", "'ca.pem'"

Socket options
~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Argument", "Description", "Default Value"

   "``--socket-path``", "Path to Docker socket (required for ``--docker-client`` socket)", "'unix:///var/run/docker.sock'"

#!/usr/bin/python3
import DOLOST

# Example of all available configurations
# To use another configuration, uncomment and modify it accordingly.

dc = from_env_config = {'from_env': True}

# dc = socket_config = {'socket': 'unix:///var/run/docker.sock'}

# dc = tcp_config = {'tcp': 'tcp://localhost:2375'}

# dc = tcp_ssl_config = {
#     'tcp_ssl': {
#         'host': 'localhost',
#         'port': 2376,
#         'cert_path': '/path/to/cert.pem',
#         'key_path': '/path/to/key.pem',
#         'ca_path': '/path/to/ca.pem'
#     }
# }

if __name__ == "__main__":
    DOLOST.start(verbosity="INFO", docker_client=dc)
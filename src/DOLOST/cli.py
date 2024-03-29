import argparse
from .app import main as start

def main():
    """
    Function to parse command-line arguments and start the DOLOST framework.

    Command-line arguments:
        --host, -H: Host to run the server on (default: '127.0.0.1')
        --port, -p: Port to run the server on (default: 9874)
        --verbosity, -v: Verbosity level ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR') (default: 'INFO')
        --docker-client, -dc: Docker client type ('tcp', 'tcp_ssl', 'socket', 'env') (default: 'env')

        TCP options:
            --tcp-host: Host for TCP connection (required for --docker-client tcp)
            --tcp-port: Port for TCP connection (required for --docker-client tcp)

        TCP+SSL options:
            --ssl-host: Host for TCP+SSL connection (required for --docker-client tcp_ssl)
            --ssl-port: Port for TCP+SSL connection (required for --docker-client tcp_ssl)
            --ssl-cert: Path to client certificate (required for --docker-client tcp_ssl)
            --ssl-key: Path to client key (required for --docker-client tcp_ssl)
            --ssl-ca: Path to CA certificate (required for --docker-client tcp_ssl)

        Socket options:
            --socket-path: Path to Docker socket (required for --docker-client socket)
    """
    parser = argparse.ArgumentParser(description='DOLOST CLI')
    parser.add_argument('--host', '-H', default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', '-p', type=int, default=9874, help='Port to run the server on')
    parser.add_argument('--verbosity', '-v', choices=['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR'], default='INFO', help='Verbosity level')
    parser.add_argument('--docker-client', '-dc', default='env', choices=['tcp', 'tcp_ssl', 'socket', 'env'], help='Docker client type')

    # TCP options
    parser.add_argument('--tcp-host', default='127.0.0.1', help='Host for TCP connection (required for --docker-client tcp)')
    parser.add_argument('--tcp-port', type=int, default=2376, help='Port for TCP connection (required for --docker-client tcp)')

    # TCP+SSL options
    parser.add_argument('--ssl-host', default='127.0.0.1', help='Host for TCP+SSL connection (required for --docker-client tcp_ssl)')
    parser.add_argument('--ssl-port', type=int, default=2376, help='Port for TCP+SSL connection (required for --docker-client tcp_ssl)')
    parser.add_argument('--ssl-cert', default='cert.pem', help='Path to client certificate (required for --docker-client tcp_ssl)')
    parser.add_argument('--ssl-key', default='key.pem', help='Path to client key (required for --docker-client tcp_ssl)')
    parser.add_argument('--ssl-ca', default='ca.pem', help='Path to CA certificate (required for --docker-client tcp_ssl)')

    # Socket options
    parser.add_argument('--socket-path', default='unix:///var/run/docker.sock', help='Path to Docker socket (required for --docker-client socket)')

    args = parser.parse_args()

    docker_client_config = {}

    if args.docker_client == 'tcp':
        docker_client_config = {'tcp': f"tcp://{args.tcp_host}:{args.tcp_port}"}
    
    elif args.docker_client == 'tcp_ssl':
        docker_client_config['tcp_ssl'] = {'host': args.ssl_host, 'port': args.ssl_port, 'cert_path': args.ssl_cert, 'key_path': args.ssl_key, 'ca_path': args.ssl_ca}
    
    elif args.docker_client == 'socket':
        docker_client_config = {'socket': args.socket_path}
    
    elif args.docker_client == 'env':
        docker_client_config = {'from_env': True}

    start(host=args.host, port=args.port, verbosity=args.verbosity, docker_client=docker_client_config)

if __name__ == '__main__':
    main()
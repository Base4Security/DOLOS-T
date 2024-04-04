from .logger import DolostLogger
from .docker_manager import DockerManager
import json
from datetime import datetime

logger = DolostLogger.get_instance()
docker_manager = DockerManager.get_instance()


class ActivityViewer:
    @staticmethod
    def review_logs():
        """
        Review logs from the activity viewer.

        This method retrieves the latest log entries from the activity viewer, specifically focusing on the logs generated by the decoys. It connects to the DolosT-Collector container, which serves as the centralized log collector for all decoys. It then tail the last 50 lines of each log file within the '/var/log/decoys/' folder, continuously monitoring for new log entries.

        Returns:
            list: A list containing the latest log entries from the activity viewer.
        """
        container_id = "DolosT-Collector"
        folder_path = "/var/log/decoys/"

        new_logs = []
        # Create a command to monitor each file within the folder continuously
        command = f"sh -c 'tail -n 50 {folder_path}*'"

        filters = {'name': [container_id]}
        CollectorExist = docker_manager.client.api.containers(filters=filters)

        # If collector doesnt exist, show a message
        if (CollectorExist):
            # Create the exec instance in the container
            exec_id = docker_manager.client.api.exec_create(container_id, command, tty=True)

            # Start streaming the output of the command
            for line in docker_manager.client.api.exec_start(exec_id['Id'], stream=True):
                log_line = line.decode().strip()  # Remove leading/trailing whitespace
                new_logs.append(log_line)

            # If no logs received, show a message
            if "tail: can't open '/var/log/decoys/*': No such file or directory\r\ntail: no files" in new_logs:
                new_logs = ["No decoy logs received in the environment yet"]
        else:
            new_logs = ["No collector deployed in the environment yet"]

        return new_logs
    
    def review_observable_ips():
        """
        Review ips found on the log files.

        This method retrieves the IPs that are found on the log entries from the collector.

        Returns:
            observable_ips: A list containing the ips and timestamps.
        """
        container_id = "DolosT-Collector"
        file_path = "/var/log/observables/observable_ips.log"
        observable_ips = []
        excluded_observable_ips = ["127.0.0.1","127.0.0.0","122.0.0.0","0.0.0.0", "200.100.0.1"]

        # Create a command to check for ips on each file
        command = f"sh -c 'cat {file_path}*'"
        filters = {'name': [container_id]}
        CollectorExist = docker_manager.client.api.containers(filters=filters)

        # If collector doesnt exist, show a message
        if (CollectorExist):
            # Create the exec instance in the container
            exec_id = docker_manager.client.api.exec_create(container_id, command, tty=True)

            # Start streaming the output of the command
            for line in docker_manager.client.api.exec_start(exec_id['Id'], stream=True):
                decoded_line = line.decode('utf-8')
                if decoded_line == ("tail: can't open '/var/log/observables/observable_ips.log*': No such file or directory\r\ntail: no files\r\n") :
                    new_ip = '{"id": 1, "decoy": "---", "ip": "No IPs","timestamp": "----" }'
                    observable_ips.append(new_ip)
                else:    
                    records = decoded_line.strip().split('\r\n')
                    # Process each record
                    i = 1
                    for record in records:
                        # Split each record by space to separate the timestamp and the IP address
                        timestamp, decoy, ip_address = record.split(',')
                        if (ip_address not in excluded_observable_ips):
                            observable_ips.append('{"id": '+ str(i) +', "decoy": "'+ decoy +'", "ip": "'+ ip_address +'", "timestamp": "' + timestamp + '"}')
                            i = i + 1
        else:
            new_ip = '{"id": 1,  "decoy": "---", "ip": "Missing Collector","timestamp": "----" }'
            observable_ips.append(new_ip)

        if (observable_ips == []):
            new_ip = '{"id": 1,  "decoy": "---", "ip": "No IPs","timestamp": "----" }'
            observable_ips.append(new_ip)
        return observable_ips

    def review_observable_usage():
        """
        Review activity found on the log files of every decoy.

        Returns:
            decoy_usage: A list containing the decoy and a count.
        """
        container_id = "DolosT-Collector"
        file_path = "/var/log/observables/observable_usage.log"
        observable_usage = []

        # Create a command to check for ips on each file
        command = f"sh -c 'cat {file_path}*'"
        filters = {'name': [container_id]}
        CollectorExist = docker_manager.client.api.containers(filters=filters)

        # If collector doesnt exist, show a message
        if (CollectorExist):
            # Create the exec instance in the container
            exec_id = docker_manager.client.api.exec_create(container_id, command, tty=True)

            # Start streaming the output of the command
            for line in docker_manager.client.api.exec_start(exec_id['Id'], stream=True):
                decoded_line = line.decode('utf-8')
                if decoded_line == ("tail: can't open '/var/log/observables/observable_usage.log*': No such file or directory\r\ntail: no files\r\n") :
                    new_data = '{"id": 1, "decoy": "No Usage data","usage": "----" }'
                    observable_usage.append(new_data)
                else:    
                    records = decoded_line.strip().split('\r\n')
                    # Process each record
                    i = 1
                    for record in records:
                        # Split each record by space to separate the timestamp and the IP address
                        usage, decoy = record.split(',')
                        observable_usage.append('{"id": '+ str(i) +', "decoy": "'+ decoy +'", "usage": "' + usage + '"}')
                        i = i + 1
        else:
            new_ip = '{"id": 1, "decoy": "Missing Collector","usage": "----" }'
            observable_usage.append(new_ip)
        
        # Auxiliar funtion to clean duplicated observables usages
        # Create a set to store unique combinations of 'decoy' and 'usage'
        seen = set()
        # Create a new list to store unique elements
        unique_data = []

        for item in observable_usage:
            # Convert string to dictionary
            item_dict = eval(item)
            
            # Get 'decoy' and 'usage' values
            decoy = item_dict['decoy']
            usage = item_dict['usage']
            
            # Check if the combination of 'decoy' and 'usage' has been seen before
            if (decoy, usage) not in seen:
                # If not seen, add it to the set of seen combinations
                seen.add((decoy, usage))
                
                # Add the original item to the new list of unique elements
                unique_data.append(item)
        observable_usage = unique_data

        return observable_usage

    def review_interesting_observable():
        """
        Review observables found on the log files.

        This method retrieves the observables that are found on the log entries from the collector.

        Returns:
            observable_interesting: A list containing the observables and timestamps.
        """
        container_id = "DolosT-Collector"
        file_path = "/var/log/observables/observable_interesting.log"
        observable_interesting = []

        # Create a command to check for observables on each file
        command = f"sh -c 'cat {file_path}*'"
        filters = {'name': [container_id]}
        CollectorExist = docker_manager.client.api.containers(filters=filters)

        # If collector doesnt exist, show a message
        if (CollectorExist):
            # Create the exec instance in the container
            exec_id = docker_manager.client.api.exec_create(container_id, command, tty=True)

            # Start streaming the output of the command
            for line in docker_manager.client.api.exec_start(exec_id['Id'], stream=True):
                decoded_line = line.decode('utf-8')
                if decoded_line == ("tail: can't open '/var/log/observables/observable_interesting.log*': No such file or directory\r\ntail: no files\r\n") :
                    new_obsercable = '{"id": 1, "decoy": "---", "interesting_data": "No Observable","timestamp": "----" }'
                    observable_interesting.append(new_obsercable)
                else:    
                    records = decoded_line.strip().split('\r\n')
                    # Process each record
                    i = 1
                    for record in records:
                        # Split each record by space to separate the timestamp and the IP address
                        timestamp, decoy, interesting_data = record.split(',')
                        observable_interesting.append('{"id": '+ str(i) +', "decoy": "'+ decoy +'", "interesting_data": "'+ interesting_data +'", "timestamp": "' + timestamp + '"}')
                        i = i + 1
        else:
            new_obsercable = '{"id": 1,  "decoy": "---", "interesting_data": "Missing Collector","timestamp": "----" }'
            observable_interesting.append(new_obsercable)

        if (observable_interesting == []):
            new_obsercable = '{"id": 1,  "decoy": "---", "interesting_data": "No Observable","timestamp": "----" }'
            observable_interesting.append(new_obsercable)
        return observable_interesting
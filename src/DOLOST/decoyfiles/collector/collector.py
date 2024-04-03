import os
import re
from datetime import datetime, timedelta
import time
from dateutil import parser

# Configuration
logs_directory = "/var/log/decoys"
ip_pattern = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
now = datetime.now()
hours_ago = now - timedelta(hours=24)
hours_ago_epoch = hours_ago.timestamp()

output_ips_file = "/var/log/observables/observable_ips.log"
output_usage_file = "/var/log/observables/observable_usage.log"
output_interesting_file = "/var/log/observables/observable_interesting.log"

# Ensure the files exists
if not os.path.exists(output_ips_file):
    open(output_ips_file, 'a').close()

if not os.path.exists(output_usage_file):
    open(output_usage_file, 'a').close()

if not os.path.exists(output_interesting_file):
    open(output_interesting_file, 'a').close()

def CheckForObservablesIps():
    # Check if the directory exists
    if os.path.isdir(logs_directory):
        # Loop through each file in the directory
        for filename in os.listdir(logs_directory):
            file_path = os.path.join(logs_directory, filename)
            # Check if the file is a regular file (not a directory or link etc.)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    for line in file:
                        # Find all IPs in the line
                        ips = ip_pattern.findall(line)
                        for ip in ips:
                            # Format the IP tuple into a string
                            ip_str = '.'.join(ip)
                            # Remove path and extension
                            decoyname = os.path.splitext(os.path.basename(file_path))[0]
                            # Check if the line (without timestamp) already exists in the output file
                            with open(output_ips_file, 'r') as output:
                                if not any(decoyname + ',' + ip_str in s for s in output):
                                    # If the line does not exist, append it with a timestamp to the file
                                    with open(output_ips_file, 'a') as output_append:
                                        output_append.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')},{decoyname},{ip_str},\n")

def CheckForObservablesUsage():
    # Clear the usage file
    with open(output_usage_file, 'w'):
        pass
    # Check if the directory exists
    if os.path.isdir(logs_directory):
        # Loop through each file in the directory
        for filename in os.listdir(logs_directory):
            file_path = os.path.join(logs_directory, filename)
            # Check if the file is a regular file (not a directory or link etc.)
            if os.path.isfile(file_path):
                count = 0
                with open(file_path, 'r') as file:
                    for line in file:
                        try:
                            # Attempt to extract and parse the timestamp from each line
                            timestamp_str = line.split()[0]  # Assuming the timestamp is the first part of each line
                            # Parse the timestamp assuming a format, adjust the format as necessary
                            line_timestamp = parser.parse(timestamp_str)
                            # Convert line timestamp to epoch
                            line_timestamp_epoch = line_timestamp.timestamp()

                            # Check if the timestamp is within the last 24 hours
                            if line_timestamp_epoch >= hours_ago_epoch:
                                count += 1
                        except ValueError:
                            # Handle cases where parsing fails
                            continue
                    # Extract the decoy name from the filename (assuming you want to strip the extension)
                    decoy_name = os.path.splitext(os.path.basename(filename))[0]

                    # Append the count and decoy name to the output file
                    with open(output_usage_file, 'a') as out_file:
                        out_file.write(f"{count},{decoy_name}\n")

def CheckForInterestingObservable():
    # Check if the directory exists
    if os.path.isdir(logs_directory):
        # Loop through each file in the directory
        for filename in os.listdir(logs_directory):
            file_path = os.path.join(logs_directory, filename)
            # Check if the file is a regular file (not a directory or link etc.)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    for line in file:
                        # Find all IPs in the line
                        if "Failed password for invalid user" in line: 
                            observable = "data"
                            decoyname = os.path.splitext(os.path.basename(file_path))[0]
                            # Check if the line (without timestamp) already exists in the output file
                            with open(output_interesting_file, 'r') as output:
                                if not any(decoyname + ',' + observable in s for s in output):
                                    # If the line does not exist, append it with a timestamp to the file
                                    with open(output_interesting_file, 'a') as output_append:
                                        output_append.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')},{decoyname},{observable},\n")

# Main
CheckForObservablesIps()
CheckForObservablesUsage()
CheckForInterestingObservable()



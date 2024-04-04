import os
import re
from datetime import datetime, timedelta
from dateutil import parser

class LogObserverBase:
    logs_directory = "/var/log/decoys"
    now = datetime.now()
    hours_ago = now - timedelta(hours=24)
    hours_ago_epoch = hours_ago.timestamp()
    syslog_regex = r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})\s+(?P<host>[\w.-]+)\s+(?P<service>\w+)\[(?P<pid>\d+)\]:\s+(?P<message>.*)'

    def __init__(self, output_file):
        self.output_file = output_file
        self.ensure_file_exists(output_file)

    @staticmethod
    def ensure_file_exists(file_path):
        if not os.path.exists(file_path):
            open(file_path, 'a').close()

    @staticmethod
    def get_file_last_line_timestamp(file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if lines:
                    last_line = lines[-1]
                    timestamp_str = last_line.split()[0]
                    return parser.parse(timestamp_str, fuzzy=True).timestamp()
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
        return None

    def is_file_relevant(self, file_timestamp_epoch):
        return file_timestamp_epoch >= self.hours_ago_epoch if file_timestamp_epoch else False

    def process_log_line(self, match):
        timestamp = match.group('timestamp')
        host = match.group('host')
        service = match.group('service')
        pid = match.group('pid')
        message = match.group('message')
        return timestamp, host, service, pid, message

    def process_file(self, file_path):
        raise NotImplementedError("Must be implemented by the subclass.")

    def run(self):
        data = []

        if os.path.isdir(self.logs_directory):
            for filename in os.listdir(self.logs_directory):
                file_path = os.path.join(self.logs_directory, filename)
                if os.path.isfile(file_path):
                    file_timestamp_epoch = self.get_file_last_line_timestamp(file_path)
                    if self.is_file_relevant(file_timestamp_epoch):
                        data.extend(self.process_file(file_path))

        # Write the sorted and limited hits to the output file
        self.after_run(data)

    def after_run(self, data):
        raise NotImplementedError("Must be implemented by the subclass.")

class ObservablesUsage(LogObserverBase):
    def process_file(self, file_path):
        hits = []
        with open(file_path, 'r') as file:
            count = sum(1 for _ in file)
        decoy_name = os.path.splitext(os.path.basename(file_path))[0]
        hits.append((count, decoy_name))
        return hits

    def after_run(self, data):
        sorted_data = sorted(data, key=lambda x: x[0], reverse=True)[:4]  # Sort by hits, limit to 5 decoys
        with open(self.output_file, 'w') as out_file:
            for count, decoy_name in sorted_data:
                out_file.write(f"{count},{decoy_name}\n")


class ObservablesIPs(LogObserverBase):
    ip_pattern = re.compile(r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")

    def process_file(self, file_path):
        hits = []

        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(self.syslog_regex, line)
                if match:
                    timestamp, _, _, _, message = self.process_log_line(match)  # Adjusted unpacking
                    ips = self.ip_pattern.findall(message)
                    decoy_name = os.path.splitext(os.path.basename(file_path))[0]
                    for ip in ips:
                        hits.append((timestamp, decoy_name, ip))

        return hits

    def after_run(self, data):
        data = sorted(data, key=lambda x: x[0], reverse=True)[:4]
        with open(self.output_file, 'w') as output:
            for hit in data:
                timestamp, decoy_name, ip = hit
                output.write(f"{timestamp}, {decoy_name}, {ip}\n")


class InterestingObservables(LogObserverBase):
    def process_file(self, file_path):
        interesting_logs = []

        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(self.syslog_regex, line)
                if match:
                    decoy_name = os.path.splitext(os.path.basename(file_path))[0]
                    timestamp, _, _, _, message = self.process_log_line(match)
                    if "Failed password for" in message:
                        interesting_logs.append((timestamp, decoy_name, message))

        return interesting_logs

    def after_run(self, data):
        # Sort the data by timestamp
        sorted_data = sorted(data, key=lambda x: x[0], reverse=True)[:4]

        # Write the sorted data to the output file
        with open(self.output_file, 'w') as out_file:
            for log_entry in sorted_data:
                out_file.write(','.join(map(str, log_entry)) + '\n')


# Update the initialization and run logic as before
if __name__ == '__main__':
    observables_ips = ObservablesIPs("/var/log/observables/observable_ips.log")
    observables_usage = ObservablesUsage("/var/log/observables/observable_usage.log")
    interesting_observables = InterestingObservables("/var/log/observables/observable_interesting.log")

    observables_ips.run()
    observables_usage.run()
    interesting_observables.run()
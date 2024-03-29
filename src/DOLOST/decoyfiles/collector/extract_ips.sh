#!/bin/sh

OUTPUT_FILE="/var/log/observables/observable_ips.log"

# Ensure the output file exists
touch "$OUTPUT_FILE"

# Tail the logs, grep for IPs, and then process each line
tail -n 50 /var/log/decoys/* | grep -oE "\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b" | while read -r line; do
    # Check if the line (without timestamp) already exists in the file
        if ! grep -qF -- "$line" "$OUTPUT_FILE"; then
        # If the line does not exist, append it with a timestamp to the file
        echo "$(date +'%Y-%m-%d %H:%M:%S') $line" >> "$OUTPUT_FILE"
    fi
done
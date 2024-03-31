#!/bin/sh

OUTPUT_FILE="/var/log/observables/observable_ips.log"

# Ensure the output file exists
touch "$OUTPUT_FILE"

# Directory containing the files
DIRECTORY="/var/log/decoys"

# Check if the directory exists
if [ -d "$DIRECTORY" ]; then
    # Loop through each file in the directory

    for file in "$DIRECTORY"/*
    do
        # Check if the file is a regular file (not a directory or link etc.)
        if [ -f "$file" ]; then
            # Tail the logs, grep for IPs, and then process each line
            cat $file | grep -oE "\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b" | while read -r line; do
                # Check if the line (without timestamp) already exists in the file
                    # Remove path and extension
                    filename=$(basename "$file")
                    decoyname="${filename%.*}"
                    if ! grep -qF -- "$decoyname,$line," "$OUTPUT_FILE"; then
                    # If the line does not exist, append it with a timestamp to the file
                    echo "$(date +'%Y-%m-%d %H:%M:%S'),$decoyname,$line," >> "$OUTPUT_FILE"
                fi
            done
        fi
    done
else
    echo "Directory does not exist: $DIRECTORY"
fi







#!/bin/sh

OUTPUT_FILE="/var/log/observables/observable_usage.log"

# Ensure the output file exists
touch "$OUTPUT_FILE"

# Directory containing the files
DIRECTORY="/var/log/decoys"

# Get the current date and time in seconds since the epoch
now=$(date +%s)

# Calculate 24 hours ago in seconds since the epoch
hours_ago=$(($now - 24*3600))

# Check if the directory exists
if [ -d "$DIRECTORY" ]; then
    # Loop through each file in the directory

    #Purge the last file
    truncate -s 0 $OUTPUT_FILE

    for file in "$DIRECTORY"/*
    do
        # Check if the file is a regular file (not a directory or link etc.)
        if [ -f "$file" ]; then
            # Count lines from the last 24 hours
            count=$(awk -v hours_ago="$hours_ago" '{
                # Extract the timestamp and convert it to seconds since the epoch
                gsub("[-T:+]", " ", $1); # Replace T and + with spaces for easier parsing
                timestamp = mktime(substr($1,1,19));

                # Check if the timestamp is within the last 24 hours
                if (timestamp >= hours_ago) {
                    count++
                }
            } END {print count}' "$file")
            # Remove path and extension
            filename=$(basename "$file")
            decoyname="${filename%.*}"            
            # Write to file
            echo "$count,$decoyname" >> "$OUTPUT_FILE"
        fi
    done
else
    echo "Directory does not exist: $DIRECTORY"
fi
#!/bin/bash

echo "Starting Brain Program..."
output=$(pros v5 run 1)
if [[ $output =~ "No v5 ports were found" ]]; then # Exits if brain is not plugged into the Jetson
    echo "BRAIN NOT PLUGGED IN... EXITING..."
    exit 1
elif [[ $output =~ "ERROR" ]]; then # Exits if other errors happen
    echo "BRAIN PROGRAM FAILED TO RUN... EXITING..."
    exit 1
fi

echo "Starting Jetson Serial Reader..."
python3 main.py

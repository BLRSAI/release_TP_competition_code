#!/bin/bash
# This script runs the entire pipeline
# This starts the pros terminal instance, Brain program and the Jetson program

tmux new-session -d bash
tmux split-window -h bash
tmux send -t 0:0.0 "./start_pros_terminal.sh" C-m
tmux send -t 0:0.1 "./start_jetson.sh" C-m
tmux -2 attach-session -d
